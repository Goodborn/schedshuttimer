import logging
import shutil
import subprocess

log = logging.getLogger(__name__)

DBUS_BUS = "org.freedesktop.login1"
DBUS_PATH = "/org/freedesktop/login1"
DBUS_IFACE = "org.freedesktop.login1.Manager"

# Ordered most- to least-graceful. login1 covers systemd AND the
# non-systemd distros that ship elogind precisely to expose this same
# D-Bus API (Artix, Void, Alpine, Gentoo/OpenRC with elogind, ...), so it
# alone covers most of the Linux landscape. The plain commands after it
# are for everything else (old SysV init, minimal containers, etc.) and
# generally need root - they're a last resort, not the happy path.
_COMMAND_FALLBACKS = (
    ["systemctl", "poweroff"],
    ["shutdown", "-h", "now"],
    ["poweroff"],
)


def _via_dbus_python() -> bool:
    try:
        import dbus
    except ImportError:
        return False
    try:
        bus = dbus.SystemBus()
        obj = bus.get_object(DBUS_BUS, DBUS_PATH)
        iface = dbus.Interface(obj, DBUS_IFACE)
        iface.PowerOff(True)
        log.info("Shutdown initiated via D-Bus (dbus-python)")
        return True
    except Exception as e:
        log.warning("D-Bus (dbus-python) shutdown failed: %s", e)
        return False


def _via_dbus_send() -> bool:
    # Same login1 call as _via_dbus_python, but shelling out to the
    # dbus-send CLI instead - it ships in the base 'dbus' package on
    # basically every distro, so this works even when dbus-python (a C
    # extension that's opt-in, see pyproject.toml) isn't installed.
    if not shutil.which("dbus-send"):
        return False
    try:
        subprocess.run(
            [
                "dbus-send", "--system", "--print-reply",
                f"--dest={DBUS_BUS}", DBUS_PATH,
                f"{DBUS_IFACE}.PowerOff", "boolean:true",
            ],
            check=True, capture_output=True, timeout=10,
        )
        log.info("Shutdown initiated via D-Bus (dbus-send)")
        return True
    except Exception as e:
        log.warning("D-Bus (dbus-send) shutdown failed: %s", e)
        return False


def _via_command(cmd: list) -> bool:
    if not shutil.which(cmd[0]):
        return False
    try:
        subprocess.run(cmd, check=True, timeout=10)
        log.info("Shutdown initiated via '%s'", " ".join(cmd))
        return True
    except Exception as e:
        log.warning("'%s' failed: %s", " ".join(cmd), e)
        return False


def shutdown() -> bool:
    """Trigger a system shutdown, trying every mechanism this machine
    might offer, most graceful first, until one actually succeeds.

    Returns True once some method reports success, False if every known
    method was unavailable or failed - callers must check this and tell
    the user, rather than assuming the machine is on its way down.
    """
    for attempt in (_via_dbus_python, _via_dbus_send):
        if attempt():
            return True
    for cmd in _COMMAND_FALLBACKS:
        if _via_command(cmd):
            return True
    log.error("No working shutdown method found on this system")
    return False


def is_available() -> bool:
    """Best-effort check for whether *any* known shutdown mechanism looks
    present, without triggering one. A binary existing doesn't guarantee
    it'll succeed without extra privileges, but this lets the UI warn the
    user up front instead of after a long countdown silently doing
    nothing.
    """
    try:
        import dbus  # noqa: F401
        return True
    except ImportError:
        pass
    if shutil.which("dbus-send"):
        return True
    return any(shutil.which(cmd[0]) for cmd in _COMMAND_FALLBACKS)
