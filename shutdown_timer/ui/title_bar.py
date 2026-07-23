from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton


class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos = None
        self.setFixedHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 12, 0)
        layout.setSpacing(0)

        title = QLabel("SHUTDOWN TIMER")
        title.setObjectName("title-label")

        self.minimize_btn = QPushButton("\u2014")
        self.minimize_btn.setFixedSize(28, 28)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #484f58;
                font-size: 12pt;
                font-weight: 300;
            }
            QPushButton:hover {
                color: #e6edf3;
                background-color: #21262d;
                border-radius: 4px;
            }
        """)
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.window().showMinimized)

        self.close_btn = QPushButton("\u2715")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #484f58;
                font-size: 10pt;
                font-weight: 400;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #da3633;
                border-radius: 4px;
            }
        """)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.window().hide)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.minimize_btn)
        layout.addSpacing(4)
        layout.addWidget(self.close_btn)

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
