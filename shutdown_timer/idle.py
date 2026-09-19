import logging
import os
import re
import shutil
import subprocess
import time

log = logging.getLogger(__name__)

# GNOME/Mutter's idle-time query - also implemented by Mutter forks (Cinnamon's
# Muffin, Budgie). Zero extra installs needed where it exists, so it's tried
# first, but it's GNOME-specific.
_MUTTER_BUS = "org.gnome.Mutter.IdleMonitor"
_MUTTER_PATH = "/org/gnome/Mutter/IdleMonitor/Core"
_MUTTER_IFACE = "org.gnome.Mutter.IdleMonitor"
_DBUS_SEND_UINT64_RE = re.compile(r"uint64\s+(\d+)")

# How often polling backends (Mutter D-Bus, xprintidle) are actually queried.
# Between polls, remaining time is extrapolated from the wall clock so the UI
# can still tick smoothly without spawning a process 4x/second.
_POLL_INTERVAL = 1.0

_SWAYIDLE_IDLE_MARKER = "__shutdown_timer_idle__"
_SWAYIDLE_RESUME_MARKER = "__shutdown_timer_resume__"


def _mutter_via_dbus_python():
    try:
        import dbus
    except ImportError:
        return None
    try:
        bus = dbus.SessionBus()
        obj = bus.get_object(_MUTTER_BUS, _MUTTER_PATH)
        iface = dbus.Interface(obj, _MUTTER_IFACE)
        return int(iface.GetIdletime()) / 1000.0
    except Exception as e:
        log.debug("Mutter IdleMonitor (dbus-python) unavailable: %s", e)
        return None


def _mutter_via_dbus_send():
    if not shutil.which("dbus-send"):
        return None
    try:
        result = subprocess.run(
            [
                "dbus-send", "--session", "--print-reply",
                f"--dest={_MUTTER_BUS}", _MUTTER_PATH,
                f"{_MUTTER_IFACE}.GetIdletime",
            ],
            check=True, capture_output=True, timeout=5, text=True,
        )
        match = _DBUS_SEND_UINT64_RE.search(result.stdout)
        return int(match.group(1)) / 1000.0 if match else None
    except Exception as e:
        log.debug("Mutter IdleMonitor (dbus-send) unavailable: %s", e)
        return None


def _mutter_idle_seconds():
    for backend in (_mutter_via_dbus_python, _mutter_via_dbus_send):
        seconds = backend()
        if seconds is not None:
            return seconds
    return None


def _xprintidle_idle_seconds():
    # X11-only (reads the XScreenSaver extension) - the fallback for
    # KDE/XFCE/i3/etc. on X11. Does nothing under Wayland.
    if not shutil.which("xprintidle"):
        return None
    try:
        result = subprocess.run(
            ["xprintidle"], check=True, capture_output=True, timeout=5, text=True,
        )
        return int(result.stdout.strip()) / 1000.0
    except Exception as e:
        log.debug("xprintidle unavailable: %s", e)
        return None


def _swayidle_usable() -> bool:
    # swayidle speaks the ext-idle-notify-v1 / org_kde_kwin_idle Wayland
    # protocols, which cover KWin, Mutter, and wlroots compositors (Sway,
    # Hyprland) alike - the only real "DE-agnostic" option under Wayland,
    # since neither of the D-Bus/X11 mechanisms above works there in
    # general (e.g. KWin advertises org.freedesktop.ScreenSaver but its
    # GetSessionIdleTime raises NotSupported on Wayland).
    return bool(os.environ.get("WAYLAND_DISPLAY")) and shutil.which("swayidle") is not None


def is_available() -> bool:
    """Best-effort check for whether idle time can be tracked at all on
    this system/session, so the UI can warn up front instead of arming a
    mode that can never trigger."""
    return (
        _mutter_idle_seconds() is not None
        or _swayidle_usable()
        or _xprintidle_idle_seconds() is not None
    )


class IdleMonitor:
    """Tracks seconds-remaining-until-idle-threshold for one armed
    inactivity-shutdown session, using whichever backend this system
    supports. One instance is used per start()/stop() cycle."""

    def __init__(self):
        if _mutter_idle_seconds() is not None:
            self._kind = "mutter"
        elif _swayidle_usable():
            self._kind = "swayidle"
        elif _xprintidle_idle_seconds() is not None:
            self._kind = "xprintidle"
        else:
            self._kind = None

        self._threshold = 0.0
        self._process = None
        self._resumed_at = 0.0
        self._triggered = False
        self._base_idle = 0.0
        self._base_time = None

    def is_available(self) -> bool:
        return self._kind is not None

    def start(self, threshold_seconds: float):
        self._threshold = threshold_seconds
        self._base_time = None
        if self._kind == "swayidle":
            self._start_swayidle(threshold_seconds)

    def _start_swayidle(self, threshold_seconds: float):
        seconds = max(1, int(round(threshold_seconds)))
        try:
            self._process = subprocess.Popen(
                [
                    "swayidle",
                    "timeout", str(seconds), f"echo {_SWAYIDLE_IDLE_MARKER}",
                    "resume", f"echo {_SWAYIDLE_RESUME_MARKER}",
                ],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            )
            os.set_blocking(self._process.stdout.fileno(), False)
        except Exception as e:
            log.warning("Failed to start swayidle: %s", e)
            self._process = None
            self._kind = None
            return
        self._resumed_at = time.monotonic()
        self._triggered = False

    def stop(self):
        if self._process is None:
            return
        self._process.terminate()
        try:
            self._process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            self._process.kill()
        self._process = None

    def remaining(self):
        """Seconds left before the idle threshold trips, or None if no
        backend is active or the running one just stopped working."""
        if self._kind == "swayidle":
            return self._remaining_swayidle()
        if self._kind in ("mutter", "xprintidle"):
            return self._remaining_polling()
        return None

    def _remaining_swayidle(self):
        if self._process is None:
            return None
        if self._process.poll() is not None:
            log.warning("swayidle exited unexpectedly (code %s)", self._process.returncode)
            self._process = None
            return None

        while True:
            try:
                line = self._process.stdout.readline()
            except BlockingIOError:
                break
            if not line:
                break
            line = line.strip()
            if line == _SWAYIDLE_RESUME_MARKER:
                self._resumed_at = time.monotonic()
                self._triggered = False
            elif line == _SWAYIDLE_IDLE_MARKER:
                self._triggered = True

        if self._triggered:
            return 0.0
        elapsed = time.monotonic() - self._resumed_at
        return max(0.0, self._threshold - elapsed)

    def _remaining_polling(self):
        now = time.monotonic()
        if self._base_time is None or (now - self._base_time) >= _POLL_INTERVAL:
            fn = _mutter_idle_seconds if self._kind == "mutter" else _xprintidle_idle_seconds
            idle_seconds = fn()
            if idle_seconds is None:
                return None
            self._base_idle = idle_seconds
            self._base_time = now

        estimated_idle = self._base_idle + (now - self._base_time)
        return max(0.0, self._threshold - estimated_idle)
