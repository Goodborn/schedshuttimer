import sys
import math
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import (
    QIcon, QAction, QPixmap, QPainter, QColor, QPen, QBrush,
    QLinearGradient, QPainterPath,
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

from shutdown_timer.ui.main_window import MainWindow
from shutdown_timer.ui.tray_icon import render_progress_icon
from shutdown_timer.style import DARK_THEME, COLORS
from shutdown_timer import __version__

_SINGLE_INSTANCE_KEY = "shutdown-timer-single-instance"

log = logging.getLogger(__name__)


def _setup_logging():
    log_dir = Path.home() / ".local" / "share" / "shutdown-timer"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "app.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )
    except OSError:
        logging.basicConfig(level=logging.INFO)


def _claim_single_instance():
    """Returns a QLocalServer kept alive for the app's lifetime, or None
    if another instance already holds the lock (caller should exit)."""
    probe = QLocalSocket()
    probe.connectToServer(_SINGLE_INSTANCE_KEY)
    already_running = probe.waitForConnected(200)
    probe.close()
    if already_running:
        return None

    QLocalServer.removeServer(_SINGLE_INSTANCE_KEY)
    server = QLocalServer()
    server.listen(_SINGLE_INSTANCE_KEY)
    return server


def _create_icon() -> QIcon:
    """Power glyph in a gap-topped ring, matching assets/icon.svg (the
    desktop-shortcut icon) so the app looks the same in the window
    decoration/taskbar as it does in the app launcher."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    cx, cy = size / 2, size / 2

    badge_grad = QLinearGradient(0, 0, size, size)
    badge_grad.setColorAt(0.0, QColor(COLORS["bg_3"]))
    badge_grad.setColorAt(0.35, QColor(COLORS["bg_2"]))
    badge_grad.setColorAt(0.7, QColor(COLORS["bg_1"]))
    badge_grad.setColorAt(1.0, QColor(COLORS["bg_0"]))
    painter.setBrush(QBrush(badge_grad))
    painter.setPen(QPen(QColor(COLORS["border"]), 1.5))
    painter.drawEllipse(QRectF(2, 2, size - 4, size - 4))

    ring_grad = QLinearGradient(12, 8, 52, 40)
    ring_grad.setColorAt(0.0, QColor(COLORS["accent_1"]))
    ring_grad.setColorAt(0.55, QColor(COLORS["accent_2"]))
    ring_grad.setColorAt(1.0, QColor(COLORS["cyan"]))
    ring_pen = QPen(QBrush(ring_grad), 6)
    ring_pen.setCapStyle(Qt.PenCapStyle.RoundCap)

    # Ring with a 70-degree gap centered on the top, so the power line
    # can "plug into" it - Qt's arc angles are in 16ths of a degree,
    # positive = counter-clockwise, 0 = 3 o'clock.
    ring_rect = QRectF(cx - 18, cy - 18, 36, 36)
    ring_path = QPainterPath()
    ring_path.arcMoveTo(ring_rect, 125)
    ring_path.arcTo(ring_rect, 125, 290)
    painter.strokePath(ring_path, ring_pen)

    painter.setPen(ring_pen)
    painter.drawLine(QPointF(cx, 6), QPointF(cx, cy - 2))

    end_x = cx + 18 * math.cos(math.radians(125))
    end_y = cy - 18 * math.sin(math.radians(125))
    painter.setBrush(QColor(COLORS["cyan"]))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(end_x - 2.6, end_y - 2.6, 5.2, 5.2))

    painter.end()
    return QIcon(pixmap)


def run() -> int:
    _setup_logging()

    app = QApplication(sys.argv)
    app.setApplicationName("Shutdown Timer")
    app.setApplicationVersion(__version__)
    app.setQuitOnLastWindowClosed(False)
    app.setStyleSheet(DARK_THEME)

    instance_lock = _claim_single_instance()
    if instance_lock is None:
        log.warning("Another instance is already running; exiting.")
        QMessageBox.information(
            None, "Shutdown Timer",
            "Shutdown Timer is already running — check your system tray.",
        )
        return 0
    # Keep the lock alive for the process lifetime.
    app._single_instance_server = instance_lock

    app_icon = _create_icon()
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.setWindowIcon(app_icon)

    tray = QSystemTrayIcon(app_icon, app)
    tray.setToolTip("Shutdown Timer")

    def restore_window():
        window.show()
        if window.isMinimized():
            window.showNormal()
        window.activateWindow()
        window.raise_()

    tray_menu = QMenu()
    show_action = QAction("Show", tray)
    show_action.triggered.connect(restore_window)

    def confirm_quit():
        if window.is_timer_active():
            box = QMessageBox(window)
            box.setIcon(QMessageBox.Icon.Warning)
            box.setWindowTitle("Shutdown Timer")
            box.setText("A shutdown timer is currently running.")
            box.setInformativeText("Quitting now will cancel it and the system will NOT shut down. Quit anyway?")
            box.setStandardButtons(QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Yes)
            box.setDefaultButton(QMessageBox.StandardButton.Cancel)
            if box.exec() != QMessageBox.StandardButton.Yes:
                return
            log.info("User quit the app while a timer was active; shutdown cancelled.")
        app.quit()

    quit_action = QAction("Quit", tray)
    quit_action.triggered.connect(confirm_quit)

    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)
    tray.setContextMenu(tray_menu)

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if window.isVisible() and not window.isMinimized():
                window.hide()
            else:
                restore_window()

    tray.activated.connect(on_tray_activated)
    tray.show()

    def on_tick_progress(remaining: int, total: int, warning: bool):
        hours, rem = divmod(remaining, 3600)
        minutes, seconds = divmod(rem, 60)
        text = f"{hours}h {minutes}m {seconds}s remaining" if hours else f"{minutes}m {seconds}s remaining"
        tray.setToolTip(text)
        tray.setIcon(render_progress_icon(remaining, total, warning))

    def reset_tray():
        tray.setIcon(app_icon)
        tray.setToolTip("Shutdown Timer")

    def on_warning_started(remaining: int):
        tray.showMessage(
            "Shutdown Timer",
            f"Shutting down in {remaining} seconds!",
            QSystemTrayIcon.MessageIcon.Warning,
            5000,
        )

    def on_shutdown_failed():
        reset_tray()
        tray.showMessage(
            "Shutdown Timer",
            "Shutdown failed — no working shutdown method on this system. "
            "The computer is still on.",
            QSystemTrayIcon.MessageIcon.Critical,
            8000,
        )
        restore_window()

    window.tick_progress.connect(on_tick_progress)
    window.timer_cancelled.connect(reset_tray)
    window.timer_finished.connect(reset_tray)
    window.warning_started.connect(on_warning_started)
    window.shutdown_failed.connect(on_shutdown_failed)

    window.show()

    log.info("Shutdown Timer started (v%s)", __version__)
    return app.exec()
