#!/usr/bin/env bash
# Installs Shutdown Timer for the current user: no sudo, no system package
# manager involved. Everything (a private venv, the launcher, the desktop
# shortcut) lands under ~/.local, so it's as easy to remove as to install
# and works the same on any distro with python3 + venv.
set -euo pipefail

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARE_DIR="$HOME/.local/share/shutdown-timer"
VENV_DIR="$SHARE_DIR/venv"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 not found - install Python 3.10+ first, then re-run this script."
    exit 1
fi

echo "==> Creating a private virtual environment"
mkdir -p "$SHARE_DIR" "$BIN_DIR" "$APPS_DIR" "$ICON_DIR"
if ! python3 -m venv "$VENV_DIR" 2>/tmp/st_venv_err.$$; then
    cat /tmp/st_venv_err.$$ >&2
    rm -f /tmp/st_venv_err.$$
    echo
    echo "Your system's Python is missing the 'venv' module. On Debian/Ubuntu:"
    echo "    sudo apt install python3-venv"
    echo "then re-run this script."
    exit 1
fi
rm -f /tmp/st_venv_err.$$

echo "==> Installing the app and its dependencies into the venv"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet "$SRC_DIR"

echo "==> Installing launcher, icon, and desktop shortcut"
cat > "$BIN_DIR/shutdown-timer" <<EOF
#!/usr/bin/env bash
exec "$VENV_DIR/bin/shutdown-timer" "\$@"
EOF
chmod +x "$BIN_DIR/shutdown-timer"

install -Dm644 "$SRC_DIR/assets/icon.svg" "$ICON_DIR/shutdown-timer.svg"
install -Dm644 "$SRC_DIR/shutdown-timer.desktop" "$APPS_DIR/shutdown-timer.desktop"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo
echo "==> Checking the optional dependency for Inactivity mode"

# Inactivity mode needs a way to read the desktop idle time; which one
# depends on the session, and unlike everything else this script installs,
# it isn't something pip can provide - it has to come from the system
# package manager. Mutter-based desktops (GNOME/Cinnamon/Budgie) need
# nothing extra (D-Bus call, always present); everything else needs one
# small package, which this installs automatically via whatever package
# manager it finds. That's the one point where this script touches the
# system instead of just $HOME - your package manager's own sudo prompt
# is the confirmation for that, same as running the install command
# yourself would be.
install_system_pkg() {
    pkg="$1"
    if command -v pacman >/dev/null 2>&1; then sudo pacman -S --noconfirm "$pkg"
    elif command -v apt-get >/dev/null 2>&1; then sudo apt-get update -qq && sudo apt-get install -y "$pkg"
    elif command -v dnf >/dev/null 2>&1; then sudo dnf install -y "$pkg"
    elif command -v zypper >/dev/null 2>&1; then sudo zypper install -y "$pkg"
    elif command -v apk >/dev/null 2>&1; then sudo apk add "$pkg"
    elif command -v eopkg >/dev/null 2>&1; then sudo eopkg install -y "$pkg"
    else
        return 1
    fi
}

idle_pkg=""
if command -v swayidle >/dev/null 2>&1 || command -v xprintidle >/dev/null 2>&1; then
    echo "    Already usable on this session."
elif [[ "${XDG_CURRENT_DESKTOP:-}" =~ (GNOME|Cinnamon|Budgie|Unity) ]]; then
    echo "    Already usable on this session (GNOME/Mutter-family D-Bus, no extra package needed)."
elif [[ -n "${WAYLAND_DISPLAY:-}" ]]; then
    idle_pkg="swayidle"
elif [[ -n "${DISPLAY:-}" ]]; then
    idle_pkg="xprintidle"
else
    echo "    No graphical session detected - skipping (re-run this script from your desktop session to pick it up)."
fi

if [[ -n "$idle_pkg" ]]; then
    echo "    Not found: '$idle_pkg' (needed for Inactivity mode on this desktop/compositor)."
    echo "    Installing it now - your package manager will prompt for your sudo password."
    if install_system_pkg "$idle_pkg"; then
        echo "    Installed $idle_pkg."
        # Recorded so uninstall.sh only removes it if *we* put it there -
        # never touches a copy that already existed for some other reason.
        echo "$idle_pkg" >> "$SHARE_DIR/.auto_installed_deps"
    else
        echo "    Couldn't install it automatically (no supported package manager found, or the"
        echo "    install failed) - install '$idle_pkg' manually to use Inactivity mode, e.g.:"
        echo "        sudo pacman -S $idle_pkg"
    fi
fi

echo
echo "================================================================"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo " Note: $BIN_DIR isn't on your PATH in this shell."
    echo " Log out/in (or open a new terminal) so the 'shutdown-timer'"
    echo " command and the app launcher both pick it up."
fi
echo " Done! Find \"Shutdown Timer\" in your app launcher, or run:"
echo "     shutdown-timer"
echo "================================================================"
