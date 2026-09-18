# SchedShutTimer

A simple shutdown scheduler for Linux, dressed up with a premium animated dark UI. Set a countdown or schedule a shutdown time with smooth animations and live visual feedback.

## Features

- **Countdown mode** — set hours, minutes, seconds with quick presets (5m, 15m, 30m, 1h)
- **Schedule mode** — pick a specific time for the system to shut down
- **System tray** — minimizes to tray with a custom icon and remaining time tooltip
- **Dark theme** — rich gradient-based dark UI with pill-shaped mode tabs and glass-morphism container

## Screenshots

![Screenshot](Screenshot.png)

## Installation

```bash
git clone https://github.com/Goodborn/schedshuttimer.git
cd schedshuttimer
./install.sh
```

Installs into a private virtual environment under `~/.local/share/shutdown-timer`,
with the `shutdown-timer` command and an app-launcher shortcut added to your
user account. No `sudo`, no system packages, nothing touches system
directories — works the same on any distro with Python 3.10+. Run it again
any time to pick up a `git pull`.

### Arch Linux (AUR)

<!-- Add AUR instructions once published -->

## Usage

```bash
shutdown-timer
```

Or directly from the source:

```bash
python -m shutdown_timer
```

### Setting a countdown

1. Select **COUNTDOWN** mode
2. Adjust hours, minutes, and seconds using the spinboxes or click a preset button
3. Click **START TIMER**
4. To cancel, click **CANCEL**

### Scheduling a shutdown

1. Select **SCHEDULE** mode
2. Pick the target shutdown time
3. Click **START TIMER**

- The app stays on top of other windows
- Close button minimizes to system tray
- The timer runs even when minimized

## How it works

SchedShutTimer tries several shutdown mechanisms in order, from most to least graceful, and uses the first one that works:

1. `org.freedesktop.login1` D-Bus (via `dbus-python`, if installed) — no password needed on an active desktop session
2. Same D-Bus call via the `dbus-send` CLI, if `dbus-python` isn't available
3. `systemctl poweroff`
4. `shutdown -h now`
5. `poweroff`

The D-Bus path (1–2) covers systemd **and** non-systemd distros that ship `elogind`, which implements the same login1 API (Artix, Void, Alpine, Gentoo/OpenRC, …) — so it's not systemd-only. The command fallbacks (3–5) cover everything else, though without a login1-style D-Bus service they generally need root.

**DE-agnostic** — works on KDE, GNOME, Hyprland, Sway, XFCE, and any other Linux desktop, since it talks to the OS, not the desktop environment.

**Guardrails:** if no shutdown mechanism can be found at all, the app refuses to arm the timer and shows a warning immediately instead of counting down to nothing. If every mechanism fails when the countdown actually hits zero (e.g. permissions changed mid-countdown), the app aborts cleanly, restores itself from the tray, and shows an error — it never silently pretends to shut down.

## Dependencies

- Python 3.10+
- PyQt6 (installed automatically by `install.sh` into its own venv)
- dbus-python (optional — only needed for the D-Bus shutdown path instead of `systemctl`)

## Building

### PKGBUILD (Arch Linux)

```bash
makepkg -si
```

## License

MIT
