from PyQt6.QtCore import Qt, QTime, QPropertyAnimation, QEasingCurve, pyqtSignal, QRect, QParallelAnimationGroup
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QSpinBox, QTimeEdit, QStackedWidget, QGraphicsOpacityEffect,
)
from PyQt6.QtGui import QFont

from shutdown_timer.ui.shimmer_button import ShimmerButton, OpacityButton

_MONO = "JetBrains Mono, Noto Sans Mono, DejaVu Sans Mono, Liberation Mono, monospace"


class CountdownPanel(QWidget):
    time_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("COUNTDOWN")
        header.setObjectName("title-label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        mono = QFont(_MONO)
        mono.setPointSize(14)
        mono.setBold(True)

        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setValue(0)
        self.hours_spin.setSuffix("h")
        self.hours_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hours_spin.setFont(mono)
        self.hours_spin.setFixedWidth(80)
        self.hours_spin.setFixedHeight(42)
        self.hours_spin.valueChanged.connect(self._emit_time)

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(30)
        self.minutes_spin.setSuffix("m")
        self.minutes_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minutes_spin.setFont(mono)
        self.minutes_spin.setFixedWidth(80)
        self.minutes_spin.setFixedHeight(42)
        self.minutes_spin.valueChanged.connect(self._emit_time)

        self.seconds_spin = QSpinBox()
        self.seconds_spin.setRange(0, 59)
        self.seconds_spin.setValue(0)
        self.seconds_spin.setSuffix("s")
        self.seconds_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.seconds_spin.setFont(mono)
        self.seconds_spin.setFixedWidth(80)
        self.seconds_spin.setFixedHeight(42)
        self.seconds_spin.valueChanged.connect(self._emit_time)

        sep1 = QLabel(":")
        sep1.setObjectName("separator")
        sep1.setFixedWidth(12)
        sep1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep2 = QLabel(":")
        sep2.setObjectName("separator")
        sep2.setFixedWidth(12)
        sep2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_row.addStretch()
        input_row.addWidget(self.hours_spin)
        input_row.addWidget(sep1)
        input_row.addWidget(self.minutes_spin)
        input_row.addWidget(sep2)
        input_row.addWidget(self.seconds_spin)
        input_row.addStretch()

        layout.addLayout(input_row)

        presets_row = QHBoxLayout()
        presets_row.setSpacing(8)

        presets = [(5, "5m"), (15, "15m"), (30, "30m"), (60, "1h")]
        self._preset_btns = []
        self._preset_minutes = []
        for minutes, label in presets:
            btn = QPushButton(label)
            btn.setObjectName("preset-btn")
            btn.setFixedSize(60, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, m=minutes: self._set_preset(m))
            presets_row.addWidget(btn)
            self._preset_btns.append(btn)
            self._preset_minutes.append(minutes)

        presets_row.insertStretch(0, 1)
        presets_row.addStretch(1)

        layout.addLayout(presets_row)
        layout.addStretch()

    def _set_preset(self, minutes: int):
        self.hours_spin.setValue(minutes // 60)
        self.minutes_spin.setValue(minutes % 60)
        self.seconds_spin.setValue(0)

        if minutes in self._preset_minutes:
            idx = self._preset_minutes.index(minutes)
            self._animate_preset_press(self._preset_btns[idx])

    def _animate_preset_press(self, btn):
        geo = btn.geometry()
        cx, cy = geo.center().x(), geo.center().y()
        anim = QPropertyAnimation(btn, b"geometry")
        anim.setDuration(250)
        anim.setStartValue(geo)
        anim.setKeyValueAt(0.3, QRect(cx - 33, cy - 16, 66, 32))
        anim.setKeyValueAt(0.6, QRect(cx - 29, cy - 14, 58, 28))
        anim.setEndValue(geo)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        anim.finished.connect(lambda: None)
        btn._press_anim = anim

    def _emit_time(self):
        total = (self.hours_spin.value() * 3600 +
                 self.minutes_spin.value() * 60 +
                 self.seconds_spin.value())
        self.time_selected.emit(total)

    def get_total_seconds(self) -> int:
        return (self.hours_spin.value() * 3600 +
                self.minutes_spin.value() * 60 +
                self.seconds_spin.value())


class IdlePanel(QWidget):
    time_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("INACTIVITY")
        header.setObjectName("title-label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        mono = QFont(_MONO)
        mono.setPointSize(14)
        mono.setBold(True)

        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setValue(0)
        self.hours_spin.setSuffix("h")
        self.hours_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hours_spin.setFont(mono)
        self.hours_spin.setFixedWidth(80)
        self.hours_spin.setFixedHeight(42)
        self.hours_spin.valueChanged.connect(self._emit_time)

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(15)
        self.minutes_spin.setSuffix("m")
        self.minutes_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minutes_spin.setFont(mono)
        self.minutes_spin.setFixedWidth(80)
        self.minutes_spin.setFixedHeight(42)
        self.minutes_spin.valueChanged.connect(self._emit_time)

        sep1 = QLabel(":")
        sep1.setObjectName("separator")
        sep1.setFixedWidth(12)
        sep1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        input_row.addStretch()
        input_row.addWidget(self.hours_spin)
        input_row.addWidget(sep1)
        input_row.addWidget(self.minutes_spin)
        input_row.addStretch()

        layout.addLayout(input_row)

        presets_row = QHBoxLayout()
        presets_row.setSpacing(8)

        presets = [(5, "5m"), (15, "15m"), (30, "30m"), (60, "1h")]
        self._preset_btns = []
        self._preset_minutes = []
        for minutes, label in presets:
            btn = QPushButton(label)
            btn.setObjectName("preset-btn")
            btn.setFixedSize(60, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, m=minutes: self._set_preset(m))
            presets_row.addWidget(btn)
            self._preset_btns.append(btn)
            self._preset_minutes.append(minutes)

        presets_row.insertStretch(0, 1)
        presets_row.addStretch(1)

        layout.addLayout(presets_row)

        info_label = QLabel("Shuts down after this much idle time")
        info_label.setObjectName("status-label")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        layout.addStretch()

    def _set_preset(self, minutes: int):
        self.hours_spin.setValue(minutes // 60)
        self.minutes_spin.setValue(minutes % 60)

        if minutes in self._preset_minutes:
            idx = self._preset_minutes.index(minutes)
            self._animate_preset_press(self._preset_btns[idx])

    def _animate_preset_press(self, btn):
        geo = btn.geometry()
        cx, cy = geo.center().x(), geo.center().y()
        anim = QPropertyAnimation(btn, b"geometry")
        anim.setDuration(250)
        anim.setStartValue(geo)
        anim.setKeyValueAt(0.3, QRect(cx - 33, cy - 16, 66, 32))
        anim.setKeyValueAt(0.6, QRect(cx - 29, cy - 14, 58, 28))
        anim.setEndValue(geo)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        anim.finished.connect(lambda: None)
        btn._press_anim = anim

    def _emit_time(self):
        total = self.hours_spin.value() * 3600 + self.minutes_spin.value() * 60
        self.time_selected.emit(total)

    def get_total_seconds(self) -> int:
        return self.hours_spin.value() * 3600 + self.minutes_spin.value() * 60


class SchedulePanel(QWidget):
    time_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        header = QLabel("SCHEDULE")
        header.setObjectName("title-label")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        font = QFont(_MONO)
        font.setPointSize(18)
        font.setBold(True)

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime().addSecs(3600))
        self.time_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_edit.setFont(font)
        self.time_edit.setFixedHeight(48)
        self.time_edit.setFixedWidth(160)
        self.time_edit.timeChanged.connect(self._emit_time)

        time_row = QHBoxLayout()
        time_row.addStretch()
        time_row.addWidget(self.time_edit)
        time_row.addStretch()
        layout.addLayout(time_row)

        info_label = QLabel("System will shut down at this time")
        info_label.setObjectName("status-label")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        layout.addStretch()

    def _emit_time(self):
        now = QTime.currentTime()
        target = self.time_edit.time()
        secs = now.secsTo(target)
        if secs < 0:
            secs += 86400
        self.time_selected.emit(secs)

    def get_total_seconds(self) -> int:
        now = QTime.currentTime()
        target = self.time_edit.time()
        secs = now.secsTo(target)
        if secs < 0:
            secs += 86400
        return secs


_MODE_NAMES = ("countdown", "schedule", "idle")


class ControlsWidget(QWidget):
    # (total_seconds, mode) where mode is "countdown", "schedule", or "idle".
    start_clicked = pyqtSignal(int, str)
    cancel_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False
        self._total_seconds = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)
        layout.setSpacing(14)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(0)

        self.btn_countdown = QPushButton("COUNTDOWN")
        self.btn_countdown.setObjectName("mode-countdown")
        self.btn_countdown.setCheckable(True)
        self.btn_countdown.setChecked(True)
        self.btn_countdown.setFixedHeight(32)
        self.btn_countdown.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_countdown.clicked.connect(lambda: self._switch_mode(0))

        self.btn_schedule = QPushButton("SCHEDULE")
        self.btn_schedule.setObjectName("mode-schedule")
        self.btn_schedule.setCheckable(True)
        self.btn_schedule.setFixedHeight(32)
        self.btn_schedule.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_schedule.clicked.connect(lambda: self._switch_mode(1))

        self.btn_idle = QPushButton("INACTIVITY")
        self.btn_idle.setObjectName("mode-idle")
        self.btn_idle.setCheckable(True)
        self.btn_idle.setFixedHeight(32)
        self.btn_idle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_idle.clicked.connect(lambda: self._switch_mode(2))

        mode_row.addWidget(self.btn_countdown)
        mode_row.addWidget(self.btn_schedule)
        mode_row.addWidget(self.btn_idle)

        layout.addLayout(mode_row)

        self.stack = QStackedWidget()
        self.countdown_panel = CountdownPanel()
        self.schedule_panel = SchedulePanel()
        self.idle_panel = IdlePanel()

        self.countdown_panel.time_selected.connect(self._on_time_changed)
        self.schedule_panel.time_selected.connect(self._on_time_changed)
        self.idle_panel.time_selected.connect(self._on_time_changed)

        self.stack.addWidget(self.countdown_panel)
        self.stack.addWidget(self.schedule_panel)
        self.stack.addWidget(self.idle_panel)
        layout.addWidget(self.stack)

        self.start_btn = ShimmerButton("START TIMER")
        self.start_btn.setObjectName("start-btn")
        self.start_btn.setFixedHeight(42)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.clicked.connect(self._on_start)

        self.cancel_btn = OpacityButton("CANCEL")
        self.cancel_btn.setObjectName("cancel-btn")
        self.cancel_btn.setFixedHeight(42)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.clicked.connect(self._on_cancel)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        self._on_time_changed(self.countdown_panel.get_total_seconds())

    def _switch_mode(self, index: int):
        if self.stack.currentIndex() == index:
            return

        self.btn_countdown.setChecked(index == 0)
        self.btn_schedule.setChecked(index == 1)
        self.btn_idle.setChecked(index == 2)

        direction = 1 if index > self.stack.currentIndex() else -1
        outgoing = self.stack.currentWidget()
        self.stack.setCurrentIndex(index)
        incoming = self.stack.currentWidget()

        self._crossfade(outgoing, incoming, direction)
        self._on_time_changed(incoming.get_total_seconds())

    def _crossfade(self, outgoing: QWidget, incoming: QWidget, direction: int):
        distance = 24 * direction

        in_effect = QGraphicsOpacityEffect(incoming)
        incoming.setGraphicsEffect(in_effect)
        in_effect.setOpacity(0.0)

        base_geo = incoming.geometry()
        incoming.setGeometry(base_geo.translated(distance, 0))

        fade_in = QPropertyAnimation(in_effect, b"opacity")
        fade_in.setDuration(280)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        slide_in = QPropertyAnimation(incoming, b"geometry")
        slide_in.setDuration(280)
        slide_in.setStartValue(base_geo.translated(distance, 0))
        slide_in.setEndValue(base_geo)
        slide_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(fade_in)
        group.addAnimation(slide_in)
        group.start()
        self._transition_anim = group

    def _on_time_changed(self, seconds: int):
        self._total_seconds = seconds
        self.start_btn.setEnabled(seconds > 0)

    def _on_start(self):
        if self._total_seconds <= 0:
            return
        self._active = True

        self._animate_button_swap(self.start_btn, self.cancel_btn)

        self.stack.setEnabled(False)
        self.btn_countdown.setEnabled(False)
        self.btn_schedule.setEnabled(False)
        self.btn_idle.setEnabled(False)
        self.start_clicked.emit(self._total_seconds, _MODE_NAMES[self.stack.currentIndex()])

    def _on_cancel(self):
        self.revert_start()
        self.cancel_clicked.emit()

    def revert_start(self):
        """Undo the visual 'started' state without emitting cancel_clicked
        - used when the app rejects the start (e.g. no shutdown/idle
        method found on this system) before a timer ever actually began,
        so the UI doesn't get stuck showing CANCEL for a timer that isn't
        running."""
        self._active = False

        self._animate_button_swap(self.cancel_btn, self.start_btn)

        self.stack.setEnabled(True)
        self.btn_countdown.setEnabled(True)
        self.btn_schedule.setEnabled(True)
        self.btn_idle.setEnabled(True)

    def _animate_button_swap(self, hide_btn, show_btn):
        fade_out = QPropertyAnimation(hide_btn, b"opacity")
        fade_out.setDuration(150)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InCubic)

        def on_done():
            hide_btn.setVisible(False)
            show_btn.setVisible(True)
            show_btn.opacity = 0.0
            fade_in = QPropertyAnimation(show_btn, b"opacity")
            fade_in.setDuration(200)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
            fade_in.start()
            self._cancel_btn_anim = fade_in

        fade_out.finished.connect(on_done)
        fade_out.start()
        self._start_btn_anim = fade_out

    def set_controls_enabled(self, enabled: bool):
        self.stack.setEnabled(enabled)
        self.btn_countdown.setEnabled(enabled)
        self.btn_schedule.setEnabled(enabled)
        self.btn_idle.setEnabled(enabled)
