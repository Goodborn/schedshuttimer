from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame,
)
from PyQt6.QtGui import QFont, QIcon, QPainter

from shutdown_timer.ui.circular_timer import CircularTimer
from shutdown_timer.ui.controls import ControlsWidget
from shutdown_timer.animations import (
    fade_in, slide_in_from_bottom, bounce_in, shake_window,
)
from shutdown_timer.shutdown import shutdown


class FadeLabel(QLabel):
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
        p.setOpacity(self._opacity)
        super().paintEvent(event)
        p.end()


class MainWindow(QMainWindow):
    timer_started = pyqtSignal()
    timer_cancelled = pyqtSignal()
    timer_finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutdown Timer")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 700)

        self._remaining = 0
        self._total = 0
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._warning_shown = False
        self._anim_refs = []

        self._status_fade_anim = None
        self._pulse_anim = None

        self._build_ui()
        self._setup_connections()

    def _build_ui(self):
        container = QFrame()
        container.setObjectName("main-container")
        container.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        title_label = QLabel("SHUTDOWN TIMER")
        title_label.setObjectName("title-label")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setContentsMargins(0, 16, 0, 0)
        layout.addWidget(title_label)

        self.status_label = FadeLabel("Set your shutdown timer")
        self.status_label.setObjectName("status-label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self.status_label)

        spacer_top = QWidget()
        spacer_top.setFixedHeight(12)
        spacer_top.setStyleSheet("background: transparent;")
        layout.addWidget(spacer_top)

        self.timer_widget = CircularTimer()
        layout.addWidget(self.timer_widget, 0, Qt.AlignmentFlag.AlignCenter)

        spacer_bottom = QWidget()
        spacer_bottom.setFixedHeight(4)
        spacer_bottom.setStyleSheet("background: transparent;")
        layout.addWidget(spacer_bottom)

        self.controls = ControlsWidget()
        layout.addWidget(self.controls)

        self.setCentralWidget(container)

    def _setup_connections(self):
        self.controls.start_clicked.connect(self._start_timer)
        self.controls.cancel_clicked.connect(self._cancel_timer)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._animate_show)

    def _animate_show(self):
        c = self.centralWidget()
        a1 = fade_in(c, 500)
        a2 = slide_in_from_bottom(self.timer_widget, 600, 30)
        a3 = bounce_in(self.controls, 500)
        self._anim_refs.extend([a1, a2, a3])
        self.centralWidget().updateGeometry()
        self.centralWidget().update()

    def _fade_status_text(self, text: str, color: str = None):
        if self._status_fade_anim and self._status_fade_anim.state() == QPropertyAnimation.State.Running:
            self._status_fade_anim.stop()

        fade_out = QPropertyAnimation(self.status_label, b"opacity")
        fade_out.setDuration(150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def on_fade_out_done():
            self.status_label.setText(text)
            if color:
                self.status_label.setStyleSheet(f"color: {color}; background: transparent;")
            else:
                self.status_label.setStyleSheet("")
            fi = QPropertyAnimation(self.status_label, b"opacity")
            fi.setDuration(250)
            fi.setStartValue(0.0)
            fi.setEndValue(1.0)
            fi.setEasingCurve(QEasingCurve.Type.OutCubic)
            fi.start()
            self._status_fade_anim = fi

        fade_out.finished.connect(on_fade_out_done)
        fade_out.start()
        self._status_fade_anim = fade_out

    def _start_timer(self, total_seconds: int):
        if total_seconds <= 0:
            return

        self._total = total_seconds
        self._remaining = total_seconds
        self._warning_shown = False
        self.timer_widget.set_total(total_seconds)
        self.timer_widget.set_remaining(total_seconds)

        self._fade_status_text("Shutting down in...")
        self._timer.start()
        self.timer_started.emit()

        a = bounce_in(self.timer_widget, 400)
        self._anim_refs.append(a)

    def _cancel_timer(self):
        self._timer.stop()
        self._remaining = 0
        self._warning_shown = False
        self.timer_widget.reset()
        self._fade_status_text("Set your shutdown timer")
        self.status_label.setStyleSheet("")
        self.timer_cancelled.emit()

    def _tick(self):
        self._remaining -= 1
        self.timer_widget.set_remaining(self._remaining)

        self._pulse_timer_tick()

        if self._remaining <= 0:
            self._timer.stop()
            self._fade_status_text("Shutting down...", "#ef4444")
            a = shake_window(self.window(), 600)
            self._anim_refs.append(a)
            QTimer.singleShot(1200, self._do_shutdown)
            return

        if self._remaining <= 10 and not self._warning_shown:
            self._warning_shown = True
            self._fade_status_text("Warning: shutting down soon!", "#ef4444")
            a = shake_window(self.window(), 400)
            self._anim_refs.append(a)

        self._update_tray_tooltip()

    def _pulse_timer_tick(self):
        if self._pulse_anim and self._pulse_anim.state() == QPropertyAnimation.State.Running:
            self._pulse_anim.stop()

        self._pulse_anim = QPropertyAnimation(self.timer_widget, b"opacity")
        self._pulse_anim.setDuration(600)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setKeyValueAt(0.15, 0.7)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pulse_anim.start()
        self._anim_refs.append(self._pulse_anim)

    def _do_shutdown(self):
        self.timer_finished.emit()
        shutdown()

    def _update_tray_tooltip(self):
        hours = self._remaining // 3600
        minutes = (self._remaining % 3600) // 60
        seconds = self._remaining % 60
        if hours > 0:
            text = f"{hours}h {minutes}m {seconds}s remaining"
        else:
            text = f"{minutes}m {seconds}s remaining"
        if hasattr(self, '_tray_callback'):
            self._tray_callback(text)

    def set_tray_callback(self, callback):
        self._tray_callback = callback

    def get_remaining(self) -> int:
        return self._remaining

    def closeEvent(self, event):
        if self._timer.isActive():
            event.ignore()
            self.hide()
        else:
            event.accept()
