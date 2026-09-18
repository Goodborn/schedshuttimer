import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QPen
from PyQt6.QtCore import Qt
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
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    painter.setBrush(QColor(COLORS["accent_0"]))
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

    window.tick_progress.connect(on_tick_progress)
    window.timer_cancelled.connect(reset_tray)
    window.timer_finished.connect(reset_tray)
    window.warning_started.connect(on_warning_started)

    window.show()

    log.info("Shutdown Timer started (v%s)", __version__)
    return app.exec()
