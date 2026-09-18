from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QRadialGradient
from PyQt6.QtWidgets import QWidget

from shutdown_timer.style import COLORS


class _Blob:
    """One slow-drifting soft-glow radial gradient."""

    def __init__(self, color: str, radius_ratio: float, path):
        self.color = QColor(color)
        self.radius_ratio = radius_ratio
        self.path = path  # list of (x_ratio, y_ratio) waypoints, 0..1
        self.t = 0.0

    def position(self, w: float, h: float):
        n = len(self.path)
        seg = self.t * n
        i = int(seg) % n
        frac = seg - int(seg)
        x0, y0 = self.path[i]
        x1, y1 = self.path[(i + 1) % n]
        x = x0 + (x1 - x0) * frac
        y = y0 + (y1 - y0) * frac
        return x * w, y * h


class AmbientBackground(QWidget):
    """Slow-drifting aurora-style glow blobs painted behind the glass
    container, for a premium, continuously-alive background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._t = 0.0

        self._blobs = [
            _Blob(COLORS["accent_0"], 0.55, [(0.15, 0.15), (0.75, 0.25), (0.65, 0.75), (0.2, 0.6)]),
            _Blob(COLORS["accent_2"], 0.5, [(0.8, 0.75), (0.25, 0.8), (0.3, 0.2), (0.75, 0.35)]),
            _Blob(COLORS["cyan"], 0.4, [(0.5, 0.9), (0.85, 0.4), (0.4, 0.1), (0.1, 0.5)]),
        ]

        self._anim = QPropertyAnimation(self, b"t")
        self._anim.setDuration(26000)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)
        self._anim.setLoopCount(-1)
        self._anim.start()

    @pyqtProperty(float)
    def t(self):
        return self._t

    @t.setter
    def t(self, val):
        self._t = val
        for i, blob in enumerate(self._blobs):
            blob.t = (val + i / len(self._blobs)) % 1.0
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        side = min(w, h)

        self._paint_card_shadow(p, w, h)

        for blob in self._blobs:
            x, y = blob.position(w, h)
            r = side * blob.radius_ratio
            grad = QRadialGradient(x, y, r)
            c = blob.color
            grad.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), 46))
            grad.setColorAt(0.6, QColor(c.red(), c.green(), c.blue(), 14))
            grad.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(grad)
            p.drawEllipse(QRectF(x - r, y - r, r * 2, r * 2))

        p.end()

    def _paint_card_shadow(self, p: QPainter, w: float, h: float):
        # Poor-man's blur: stacked rounded rects fading outward, offset
        # down slightly. Mirrors the card_wrap's 10px inset + 22px radius.
        base = QRectF(10, 10, w - 20, h - 20)
        layers = 10
        for i in range(layers, 0, -1):
            spread = i * 2.2
            alpha = int(9 * (1 - i / (layers + 2)))
            rect = base.adjusted(-spread, -spread + 4, spread, spread + 4)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(0, 0, 0, max(2, alpha)))
            p.drawRoundedRect(rect, 22 + spread, 22 + spread)
