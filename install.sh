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
echo "================================================================"
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo " Note: $BIN_DIR isn't on your PATH in this shell."
    echo " Log out/in (or open a new terminal) so the 'shutdown-timer'"
    echo " command and the app launcher both pick it up."
fi
echo " Done! Find \"Shutdown Timer\" in your app launcher, or run:"
echo "     shutdown-timer"
echo "================================================================"
