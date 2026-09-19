import logging
import time

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QFrame,
    QStackedLayout, QGraphicsOpacityEffect,
)

from shutdown_timer.ui.circular_timer import CircularTimer
from shutdown_timer.ui.controls import ControlsWidget
from shutdown_timer.ui.title_bar import TitleBar
from shutdown_timer.ui.ambient_background import AmbientBackground
from shutdown_timer.animations import (
    slide_in_from_bottom, bounce_in, shake_window,
)
from shutdown_timer.shutdown import shutdown, is_available
from shutdown_timer import idle
from shutdown_timer.style import COLORS

# Grace period between the countdown hitting zero and the actual shutdown
# call, purely so the "shutting down..." animation is visible. Must stay
# cancellable right up to the last moment (see _cancel_timer).
_SHUTDOWN_GRACE_MS = 1200

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    timer_started = pyqtSignal()
    timer_cancelled = pyqtSignal()
    timer_finished = pyqtSignal()
    # (remaining_seconds, total_seconds, warning_active) - emitted every
    # tick so the tray icon can animate in lockstep with the on-window timer.
    tick_progress = pyqtSignal(int, int, bool)
    # Fired once, the instant the last-10-seconds warning state begins.
    warning_started = pyqtSignal(int)
    # Fired when the countdown hit zero but no shutdown mechanism actually
    # worked (unsupported/locked-down system) - the machine is NOT going down.
    shutdown_failed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutdown Timer")
        # No Qt.WindowType.Tool: that hint hides the window from the
        # taskbar entirely, which breaks "minimize to taskbar" (there'd be
        # nothing to click to restore it). Close still goes to tray via
        # closeEvent below; minimize now does a real OS minimize.
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(420, 720)

        self._remaining = 0
        self._total = 0
        self._deadline = None  # wall-clock time.time() the shutdown is due
        self._idle_mode = False
        self._idle_monitor = None
        self._timer = QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._tick)
        self._warning_shown = False
        self._anim_refs = []

        self._shutdown_pending_timer = QTimer(self)
        self._shutdown_pending_timer.setSingleShot(True)
        self._shutdown_pending_timer.timeout.connect(self._do_shutdown)

        self._status_fade_anim = None
        self._pulse_anim = None

        self._build_ui()
        self._setup_connections()

    def _build_ui(self):
        # Root stack: ambient animated background painted beneath the
        # glass panel, both filling the frameless window.
        root = QWidget()
        root_layout = QStackedLayout(root)
        root_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.ambient = AmbientBackground()
        root_layout.addWidget(self.ambient)

        card_wrap = QWidget()
        card_wrap.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        card_wrap_layout = QVBoxLayout(card_wrap)
        card_wrap_layout.setContentsMargins(10, 10, 10, 10)

        container = QFrame()
        container.setObjectName("main-container")
        container.setFrameShape(QFrame.Shape.NoFrame)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 16)
        layout.setSpacing(0)

        self.title_bar = TitleBar()
        layout.addWidget(self.title_bar)

        self.status_label = QLabel("Set your shutdown timer")
        self.status_label.setObjectName("status-label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setContentsMargins(0, 10, 0, 2)
        self._status_opacity_effect = QGraphicsOpacityEffect(self.status_label)
        self._status_opacity_effect.setOpacity(1.0)
        self.status_label.setGraphicsEffect(self._status_opacity_effect)
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

        card_wrap_layout.addWidget(container)
        root_layout.addWidget(card_wrap)
        self.card_wrap = card_wrap
        self.setCentralWidget(root)

    def _setup_connections(self):
        self.controls.start_clicked.connect(self._start_timer)
        self.controls.cancel_clicked.connect(self._cancel_timer)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._animate_show)

    def _animate_show(self):
        # Geometry-only entrance, deliberately not opacity-based: Qt's
        # Wayland platform plugin doesn't support setWindowOpacity() at
        # all, and a QGraphicsOpacityEffect on an ancestor of the
        # continuously self-animating CircularTimer makes PyQt6 open
        # overlapping QPainters on it (its render() pass races the
        # widget's own paint updates). A geometry animation has neither
        # problem and works identically everywhere.
        a1 = bounce_in(self.card_wrap, 500)
        a2 = slide_in_from_bottom(self.timer_widget, 600, 30)
        a3 = bounce_in(self.controls, 500)
        self._anim_refs.extend([a1, a2, a3])
        self.centralWidget().updateGeometry()
        self.centralWidget().update()

    def _fade_status_text(self, text: str, color: str = None):
        if self._status_fade_anim and self._status_fade_anim.state() == QPropertyAnimation.State.Running:
            self._status_fade_anim.stop()

        fade_out = QPropertyAnimation(self._status_opacity_effect, b"opacity")
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
            fi = QPropertyAnimation(self._status_opacity_effect, b"opacity")
            fi.setDuration(250)
            fi.setStartValue(0.0)
            fi.setEndValue(1.0)
            fi.setEasingCurve(QEasingCurve.Type.OutCubic)
            fi.start()
            self._status_fade_anim = fi

        fade_out.finished.connect(on_fade_out_done)
        fade_out.start()
        self._status_fade_anim = fade_out

    def _start_timer(self, total_seconds: int, mode: str = "countdown"):
        if total_seconds <= 0:
            return

        if not is_available():
            # Guardrail: warn now rather than let the user walk away from
            # a multi-hour countdown that can never actually shut anything
            # down (no systemd-logind/elogind D-Bus, no systemctl/shutdown/
            # poweroff binary found anywhere on PATH).
            self._fade_status_text("No shutdown method found on this system", COLORS["danger_1"])
            a = shake_window(self.window(), 400)
            self._anim_refs.append(a)
            self.controls.revert_start()
            return

        self._idle_mode = mode == "idle"
        if self._idle_mode:
            self._idle_monitor = idle.IdleMonitor()
            # is_available() is a cheap up-front check (binary + session
            # type); start() can still fail (e.g. the compositor doesn't
            # actually implement any idle protocol swayidle speaks), so
            # both are treated as the same "can't track idle time" case.
            started = self._idle_monitor.is_available() and self._idle_monitor.start(total_seconds)
            if not started:
                self._fade_status_text("No idle-detection method found on this system", COLORS["danger_1"])
                a = shake_window(self.window(), 400)
                self._anim_refs.append(a)
                self._idle_mode = False
                self._idle_monitor = None
                self.controls.revert_start()
                return

        self._total = total_seconds
        self._remaining = total_seconds
        # Wall-clock deadline rather than a pure tick-decrement: stays
        # accurate even if the event loop stalls or the system suspends
        # and resumes mid-countdown (real time keeps passing either way).
        # Unused in idle mode, where remaining comes from the idle monitor.
        self._deadline = time.time() + total_seconds
        self._warning_shown = False
        self.timer_widget.set_total(total_seconds)
        self.timer_widget.set_remaining(total_seconds)

        self._fade_status_text("Shutting down after inactivity..." if self._idle_mode else "Shutting down in...")
        self._timer.start()
        self.title_bar.set_armed(True)
        self.timer_started.emit()

        a = bounce_in(self.timer_widget, 400)
        self._anim_refs.append(a)

    def _cancel_timer(self):
        self._timer.stop()
        self._shutdown_pending_timer.stop()
        self._stop_idle_monitor()
        self._remaining = 0
        self._deadline = None
        self._warning_shown = False
        self.timer_widget.reset()
        self._fade_status_text("Set your shutdown timer")
        self.status_label.setStyleSheet("")
        self.title_bar.set_armed(False)
        self.timer_cancelled.emit()

    def _stop_idle_monitor(self):
        if self._idle_monitor is not None:
            self._idle_monitor.stop()
            self._idle_monitor = None
        self._idle_mode = False

    def _tick(self):
        if self._idle_mode:
            remaining = self._idle_monitor.remaining()
            if remaining is None:
                # The idle backend stopped working mid-run (e.g. swayidle
                # crashed) - stay conservative and hold position rather
                # than guessing, but let the user know something's wrong.
                log.warning("Idle-time source stopped responding; timer held")
                return
            self._remaining = int(round(remaining))
        else:
            self._remaining = max(0, int(round(self._deadline - time.time())))
        self.timer_widget.set_remaining(self._remaining)

        self._pulse_timer_tick()

        if self._remaining <= 0:
            self._timer.stop()
            self._fade_status_text("Shutting down...", COLORS["danger_1"])
            a = shake_window(self.window(), 600)
            self._anim_refs.append(a)
            self.tick_progress.emit(0, self._total, True)
            self._shutdown_pending_timer.start(_SHUTDOWN_GRACE_MS)
            return

        if self._remaining <= 10 and not self._warning_shown:
            self._warning_shown = True
            self._fade_status_text("Warning: shutting down soon!", COLORS["danger_1"])
            a = shake_window(self.window(), 400)
            self._anim_refs.append(a)
            self.warning_started.emit(self._remaining)

        self.tick_progress.emit(self._remaining, self._total, self._warning_shown)

    def _pulse_timer_tick(self):
        if self._pulse_anim and self._pulse_anim.state() == QPropertyAnimation.State.Running:
            return

        self._pulse_anim = QPropertyAnimation(self.timer_widget, b"opacity")
        self._pulse_anim.setDuration(900)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setKeyValueAt(0.15, 0.85)
        self._pulse_anim.setEndValue(1.0)
        self._pulse_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._pulse_anim.start()

    def _do_shutdown(self):
        self._stop_idle_monitor()

        if shutdown():
            self.timer_finished.emit()
            return

        # Every known shutdown mechanism failed - the machine is staying
        # up, so unwind back to an idle state instead of leaving the UI
        # stuck showing "Shutting down..." forever.
        self._remaining = 0
        self._deadline = None
        self._warning_shown = False
        self.timer_widget.reset()
        self.title_bar.set_armed(False)
        self._fade_status_text("Shutdown failed — check permissions/logs", COLORS["danger_1"])
        a = shake_window(self.window(), 600)
        self._anim_refs.append(a)
        self.shutdown_failed.emit()

    def cleanup(self):
        """Called on real app quit (see app.py's aboutToQuit) - without
        this, an active idle-mode session would leak its swayidle
        subprocess as an orphan once this process exits."""
        self._stop_idle_monitor()

    def get_remaining(self) -> int:
        return self._remaining

    def is_timer_active(self) -> bool:
        return self._timer.isActive() or self._shutdown_pending_timer.isActive()

    def closeEvent(self, event):
        # Always minimize-to-tray rather than actually closing: this is a
        # frameless Tool window with no taskbar entry, so a real close/
        # minimize would leave no way to bring it back except the tray icon.
        event.ignore()
        self.hide()
