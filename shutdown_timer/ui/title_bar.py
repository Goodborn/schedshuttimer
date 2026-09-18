from PyQt6.QtCore import Qt, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QRadialGradient
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from shutdown_timer.style import COLORS


class _StatusDot(QWidget):
    """Small breathing dot that mirrors the app's idle/armed state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(8, 8)
        self._glow = 0.4
        self._color = QColor(COLORS["text_muted"])

        self._anim = QPropertyAnimation(self, b"glow")
        self._anim.setDuration(1600)
        self._anim.setStartValue(0.35)
        self._anim.setKeyValueAt(0.5, 1.0)
        self._anim.setEndValue(0.35)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)
        self._anim.start()

    @pyqtProperty(float)
    def glow(self):
        return self._glow

    @glow.setter
    def glow(self, val):
        self._glow = val
        self.update()

    def set_armed(self, armed: bool):
        self._color = QColor(COLORS["danger_1"] if armed else COLORS["accent_1"])
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx, cy = self.width() / 2, self.height() / 2
        r = self.width() / 2

        glow_r = r * (1.4 + 0.8 * self._glow)
        grad = QRadialGradient(cx, cy, glow_r)
        grad.setColorAt(0.0, QColor(self._color.red(), self._color.green(), self._color.blue(),
                                     int(160 * self._glow)))
        grad.setColorAt(1.0, QColor(self._color.red(), self._color.green(), self._color.blue(), 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(grad)
        p.drawEllipse(self.rect().adjusted(-int(glow_r), -int(glow_r), int(glow_r), int(glow_r)))

        p.setBrush(self._color)
        p.drawEllipse(self.rect())
        p.end()


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("title-bar")
        self._drag_pos = None
        self.setFixedHeight(44)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 0, 12, 0)
        layout.setSpacing(8)

        self.status_dot = _StatusDot()

        title = QLabel("SHUTDOWN TIMER")
        title.setObjectName("brand-label")

        # padding/min-width/min-height explicitly zeroed: the app-wide
        # QSS sets QPushButton { padding: 7px 18px } which cascades into
        # any per-widget stylesheet that doesn't override it, and on a
        # 28x24 button that padding alone exceeds the button's size and
        # crushes the glyph out of the visible area.
        btn_style = """
            QPushButton {{
                border: none;
                background: transparent;
                color: {muted};
                font-size: 11pt;
                font-weight: 400;
                border-radius: 6px;
                padding: 0px;
                min-width: 0px;
                min-height: 0px;
            }}
            QPushButton:hover {{
                color: {hover_fg};
                background-color: {hover_bg};
            }}
        """

        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(28, 24)
        self.minimize_btn.setStyleSheet(btn_style.format(
            muted=COLORS["text_muted"], hover_fg=COLORS["text_primary"], hover_bg=COLORS["border_soft"],
        ))
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.clicked.connect(lambda: self.window().showMinimized())

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(28, 24)
        self.close_btn.setStyleSheet(btn_style.format(
            muted=COLORS["text_muted"], hover_fg="#ffffff", hover_bg=COLORS["danger_0"],
        ))
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(lambda: self.window().close())

        layout.addWidget(self.status_dot)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)

    def set_armed(self, armed: bool):
        self.status_dot.set_armed(armed)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos:
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def mouseDoubleClickEvent(self, event):
        if self.window().isMinimized():
            self.window().showNormal()
        else:
            self.window().showMinimized()
