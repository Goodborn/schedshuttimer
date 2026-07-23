import sys
import os
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QSize

from shutdown_timer.ui.main_window import MainWindow
from shutdown_timer.style import DARK_THEME
from shutdown_timer import __version__


def _create_icon() -> QIcon:
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor("#1f6feb"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, size - 8, size - 8)

    painter.setPen(QPen(QColor("#ffffff"), 3))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    cx, cy = size // 2, size // 2
    painter.drawEllipse(cx - 18, cy - 18, 36, 36)

    painter.setPen(QPen(QColor("#ffffff"), 2.5))
    painter.drawLine(cx, cy, cx, cy - 12)
    painter.drawLine(cx, cy, cx + 9, cy + 2)

    painter.end()
    return QIcon(pixmap)


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Shutdown Timer")
    app.setApplicationVersion(__version__)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(DARK_THEME)

    app_icon = _create_icon()
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.setWindowIcon(app_icon)

    tray = QSystemTrayIcon(app_icon, app)
    tray.setToolTip("Shutdown Timer")

    tray_menu = QMenu()
    show_action = QAction("Show", tray)
    show_action.triggered.connect(lambda: (window.show(), window.activateWindow()))
    quit_action = QAction("Quit", tray)
    quit_action.triggered.connect(app.quit)

    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    tray.setContextMenu(tray_menu)

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if window.isVisible():
                window.hide()
            else:
                window.show()
                window.activateWindow()

    tray.activated.connect(on_tray_activated)
    tray.show()

    def update_tray(text):
        tray.setToolTip(text)

    window.set_tray_callback(update_tray)

    window.show()

    return app.exec()
