#!/usr/bin/env bash
# Removes everything install.sh created: the private venv, launcher,
# desktop shortcut, and icon. If install.sh auto-installed a system
# package for Inactivity mode (swayidle/xprintidle), this removes that
# too - but only a package install.sh itself installed, never one that
# was already on the system for some other reason.
set -euo pipefail

SHARE_DIR="$HOME/.local/share/shutdown-timer"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
DEPS_MARKER="$SHARE_DIR/.auto_installed_deps"

remove_system_pkg() {
    pkg="$1"
    if command -v pacman >/dev/null 2>&1; then sudo pacman -R --noconfirm "$pkg"
    elif command -v apt-get >/dev/null 2>&1; then sudo apt-get remove -y "$pkg"
    elif command -v dnf >/dev/null 2>&1; then sudo dnf remove -y "$pkg"
    elif command -v zypper >/dev/null 2>&1; then sudo zypper remove -y "$pkg"
    elif command -v apk >/dev/null 2>&1; then sudo apk del "$pkg"
    elif command -v eopkg >/dev/null 2>&1; then sudo eopkg remove -y "$pkg"
    else
        return 1
    fi
}

if [[ -f "$DEPS_MARKER" ]]; then
    echo "==> Removing dependencies installed automatically alongside Shutdown Timer"
    while IFS= read -r pkg; do
        [[ -z "$pkg" ]] && continue
        echo "    Removing '$pkg' (your package manager will prompt for your sudo password)"
        if ! remove_system_pkg "$pkg"; then
            echo "    Couldn't remove '$pkg' automatically - remove it yourself if you no longer want it."
        fi
    done < "$DEPS_MARKER"
    # pacman/apt etc. refuse to remove a package something else still
    # depends on, so this is safe even if another app has since started
    # using it too.
fi

echo "==> Removing Shutdown Timer"
rm -f "$BIN_DIR/shutdown-timer"
rm -f "$APPS_DIR/shutdown-timer.desktop"
rm -f "$ICON_DIR/shutdown-timer.svg"
rm -rf "$SHARE_DIR"

command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS_DIR" || true
command -v gtk-update-icon-cache >/dev/null 2>&1 && gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

echo "Done. Shutdown Timer has been removed."
