import time

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen

from shutdown_timer.style import COLORS

_SIZE = 64
_FLASH_HZ = 2.0  # how fast the icon blinks during the last-10-seconds warning


def render_progress_icon(remaining: int, total: int, warning: bool) -> QIcon:
    """A small ring icon mirroring the main window's circular timer:
    fills clockwise as time elapses, recolors by how much is left, and
    blinks red once inside the last-10-seconds warning window."""
    pixmap = QPixmap(_SIZE, _SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)

    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx = cy = _SIZE / 2
    radius = _SIZE / 2 - 6

    progress = (remaining / total) if total else 0.0
    flash_on = warning and (int(time.time() * _FLASH_HZ * 2) % 2 == 0)

    if flash_on:
        accent = QColor(COLORS["danger_1"])
    elif progress > 0.5:
        accent = QColor(COLORS["success_1"])
    elif progress > 0.2:
        accent = QColor(COLORS["warning"])
    else:
        accent = QColor(COLORS["danger_1"])

    track_pen = QPen(QColor(COLORS["border_soft"]), 7)
    track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(track_pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    if progress > 0:
        pen = QPen(accent, 8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        span = int(progress * 360 * 16)
        p.drawArc(QRectF(cx - radius, cy - radius, radius * 2, radius * 2), 90 * 16, -span)

    if warning:
        # Filled center disc during the final countdown, on top of the
        # ring, so the blink reads clearly even at tray-icon size.
        fill = QColor(accent)
        fill.setAlpha(255 if flash_on else 90)
        p.setBrush(fill)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QRectF(cx - radius * 0.45, cy - radius * 0.45, radius * 0.9, radius * 0.9))

    p.end()
    return QIcon(pixmap)
