from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import QPushButton

from shutdown_timer.style import COLORS


class _AnimatedGradientButton(QPushButton):
    """Base for pill buttons that paint their own animated gradient
    (native QSS background is skipped so the gradient/opacity/press
    animations stay perfectly in sync). Glow is hand-painted rather than
    a QGraphicsDropShadowEffect: PyQt6 chokes on that effect combined
    with a manual QPainter(self) in paintEvent (paint-device conflict)."""

    def __init__(self, text="", gradient_stops=None, glow_color="#000000", parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0
        self._press_scale = 1.0
        self._gradient_stops = gradient_stops or [(0.0, "#334155"), (1.0, "#475569")]
        self._glow_color = QColor(glow_color)

        self._press_anim = QPropertyAnimation(self, b"press_scale")
        self._press_anim.setDuration(280)
        self._press_anim.setEasingCurve(QEasingCurve.Type.OutElastic)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()

    @pyqtProperty(float)
    def press_scale(self):
        return self._press_scale

    @press_scale.setter
    def press_scale(self, val):
        self._press_scale = val
        self.update()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self._press_anim.stop()
        self._press_anim.setStartValue(0.94)
        self._press_anim.setEndValue(1.0)
        self._press_anim.start()

    def _paint_glow(self, p: QPainter, rect: QRectF):
        if not self.isEnabled():
            return
        glow_rect = rect.adjusted(-10, -6, 10, 10)
        grad = QRadialGradient(rect.center(), rect.width() * 0.65)
        c = self._glow_color
        grad.setColorAt(0.0, QColor(c.red(), c.green(), c.blue(), 60))
        grad.setColorAt(1.0, QColor(c.red(), c.green(), c.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(glow_rect, glow_rect.height() / 2, glow_rect.height() / 2)

    def _paint_base(self, p: QPainter):
        rect = QRectF(self.rect())
        if self._press_scale != 1.0:
            cx, cy = rect.center().x(), rect.center().y()
            w, h = rect.width() * self._press_scale, rect.height() * self._press_scale
            rect = QRectF(cx - w / 2, cy - h / 2, w, h)

        self._paint_glow(p, rect)

        radius = rect.height() / 2

        grad = QLinearGradient(rect.topLeft(), rect.topRight())
        for pos, color in self._gradient_stops:
            grad.setColorAt(pos, QColor(color))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawRoundedRect(rect, radius, radius)
        return rect


class OpacityButton(_AnimatedGradientButton):
    """Secondary/destructive pill button (Cancel)."""

    def __init__(self, text="", parent=None):
        super().__init__(
            text,
            gradient_stops=[(0.0, COLORS["danger_0"]), (0.5, COLORS["danger_1"]), (1.0, COLORS["danger_2"])],
            glow_color=COLORS["danger_1"],
            parent=parent,
        )

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self._opacity * (1.0 if self.isEnabled() else 0.35))

        rect = self._paint_base(p)

        font = QFont(self.font())
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor("#ffffff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()


class ShimmerButton(_AnimatedGradientButton):
    """Primary action pill button (Start) with an animated light sweep."""

    def __init__(self, text="", parent=None):
        super().__init__(
            text,
            gradient_stops=[(0.0, COLORS["success_0"]), (0.5, COLORS["success_1"]), (1.0, COLORS["success_2"])],
            glow_color=COLORS["success_1"],
            parent=parent,
        )
        self._shimmer_x = -0.3
        self._pulse_scale = 1.0

        self.shimmer_anim = QPropertyAnimation(self, b"shimmer_x")
        self.shimmer_anim.setDuration(2600)
        self.shimmer_anim.setStartValue(-0.3)
        self.shimmer_anim.setEndValue(1.3)
        self.shimmer_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.shimmer_anim.setLoopCount(-1)

        self.pulse_anim = QPropertyAnimation(self, b"pulse_scale")
        self.pulse_anim.setDuration(1800)
        self.pulse_anim.setStartValue(1.0)
        self.pulse_anim.setKeyValueAt(0.5, 1.02)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_anim.setLoopCount(-1)

        self.shimmer_anim.start()
        self.pulse_anim.start()

    @pyqtProperty(float)
    def shimmer_x(self):
        return self._shimmer_x

    @shimmer_x.setter
    def shimmer_x(self, val):
        self._shimmer_x = val
        self.update()

    @pyqtProperty(float)
    def pulse_scale(self):
        return self._pulse_scale

    @pulse_scale.setter
    def pulse_scale(self, val):
        self._pulse_scale = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self._opacity * (1.0 if self.isEnabled() else 0.35))

        rect = self._paint_base(p)

        shimmer_w = rect.width() * 0.35
        shimmer_x = rect.x() + self._shimmer_x * rect.width()
        gradient = QLinearGradient(shimmer_x, 0, shimmer_x + shimmer_w, 0)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 55))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(gradient)
        p.drawRoundedRect(rect, rect.height() / 2, rect.height() / 2)

        font = QFont(self.font())
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor("#ffffff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        p.end()
