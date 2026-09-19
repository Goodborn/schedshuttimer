# Maintainer: goodborn <goodborn@archlinux>
pkgname=shutdown-timer
pkgver=1.0.0
pkgrel=1
pkgdesc="Heavily animated shutdown timer with PyQt6"
arch=('any')
url="https://github.com/goodborn/ShutdownTimer"
license=('MIT')
depends=(
  'python'
  'python-pyqt6'
  'qt6-base'
)
optdepends=(
  'python-dbus: shutdown via D-Bus instead of the systemctl fallback'
  'swayidle: inactivity mode on KWin/Hyprland/Sway/Niri and other Wayland compositors'
  'xprintidle: inactivity mode on X11 sessions (KDE, XFCE, i3, ...)'
)
makedepends=(
  'python-build'
  'python-installer'
  'python-hatchling'
)
source=("$pkgname-$pkgver.tar.gz::https://github.com/goodborn/ShutdownTimer/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
  cd "$srcdir/ShutdownTimer-$pkgver"
  python -m build --wheel --no-isolation
}

package() {
  cd "$srcdir/ShutdownTimer-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl

  install -Dm644 "$srcdir/ShutdownTimer-$pkgver/assets/icon.svg" \
    "$pkgdir/usr/share/icons/hicolor/scalable/apps/shutdown-timer.svg"
  install -Dm644 "$srcdir/ShutdownTimer-$pkgver/shutdown-timer.desktop" \
    "$pkgdir/usr/share/applications/shutdown-timer.desktop"
}
