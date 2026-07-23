from PyQt6.QtCore import Qt, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient
from PyQt6.QtWidgets import QPushButton


class OpacityButton(QPushButton):
    """QPushButton that supports animated opacity via a native property."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._opacity = 1.0

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self._opacity)
        super().paintEvent(event)
        p.end()


class ShimmerButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._shimmer_x = -0.3
        self._pulse_scale = 1.0
        self._opacity = 1.0

        self.shimmer_anim = QPropertyAnimation(self, b"shimmer_x")
        self.shimmer_anim.setDuration(2500)
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

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self._opacity)

        rect = QRectF(self.rect())

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#238636"))
        p.drawRoundedRect(rect, 10, 10)

        shimmer_w = rect.width() * 0.4
        shimmer_x = rect.x() + self._shimmer_x * rect.width()
        gradient = QLinearGradient(shimmer_x, 0, shimmer_x + shimmer_w, 0)
        gradient.setColorAt(0.0, QColor(255, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(255, 255, 255, 30))
        gradient.setColorAt(1.0, QColor(255, 255, 255, 0))
        p.setBrush(gradient)
        p.drawRoundedRect(rect, 10, 10)

        font = QFont(self.font())
        font.setWeight(QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QColor("#ffffff"))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())

        p.end()
