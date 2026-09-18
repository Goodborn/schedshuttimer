import math
from PyQt6.QtCore import Qt, QSize, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QRadialGradient, QConicalGradient
from PyQt6.QtWidgets import QWidget, QSizePolicy

from shutdown_timer.style import COLORS

_ACCENT = QColor(COLORS["accent_1"])
_ACCENT_RGB = (_ACCENT.red(), _ACCENT.green(), _ACCENT.blue())


class CircularTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0
        self._remaining = 0
        self._total = 1
        self._glow_intensity = 0.0
        self._warning_mode = False
        self._rotation = 0.0
        self._idle_rotation = 0.0
        self._idle_glow = 0.0
        self._ready_pulse = 0.0
        self._opacity = 1.0
        self._center_glow = 0.0
        self._orbital_angle = 0.0
        self.setMinimumSize(280, 280)
        self.setMaximumSize(280, 280)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.progress_anim = QPropertyAnimation(self, b"progress")
        self.progress_anim.setEasingCurve(QEasingCurve.Type.Linear)

        self.glow_anim = QPropertyAnimation(self, b"glow_intensity")
        self.glow_anim.setDuration(1500)
        self.glow_anim.setStartValue(0.3)
        self.glow_anim.setKeyValueAt(0.5, 1.0)
        self.glow_anim.setEndValue(0.3)
        self.glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        self.rotation_anim = QPropertyAnimation(self, b"rotation")
        self.rotation_anim.setDuration(3000)
        self.rotation_anim.setStartValue(0.0)
        self.rotation_anim.setEndValue(360.0)
        self.rotation_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.rotation_anim.setLoopCount(-1)

        self.idle_rot_anim = QPropertyAnimation(self, b"idle_rotation")
        self.idle_rot_anim.setDuration(25000)
        self.idle_rot_anim.setStartValue(0.0)
        self.idle_rot_anim.setEndValue(360.0)
        self.idle_rot_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.idle_rot_anim.setLoopCount(-1)
        self.idle_rot_anim.start()

        self.idle_glow_anim = QPropertyAnimation(self, b"idle_glow")
        self.idle_glow_anim.setDuration(3000)
        self.idle_glow_anim.setStartValue(0.0)
        self.idle_glow_anim.setKeyValueAt(0.5, 1.0)
        self.idle_glow_anim.setEndValue(0.0)
        self.idle_glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.idle_glow_anim.setLoopCount(-1)
        self.idle_glow_anim.start()

        self.ready_pulse_anim = QPropertyAnimation(self, b"ready_pulse")
        self.ready_pulse_anim.setDuration(2500)
        self.ready_pulse_anim.setStartValue(0.2)
        self.ready_pulse_anim.setKeyValueAt(0.5, 1.0)
        self.ready_pulse_anim.setEndValue(0.2)
        self.ready_pulse_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.ready_pulse_anim.setLoopCount(-1)
        self.ready_pulse_anim.start()

        self.center_glow_anim = QPropertyAnimation(self, b"center_glow")
        self.center_glow_anim.setDuration(4000)
        self.center_glow_anim.setStartValue(0.0)
        self.center_glow_anim.setKeyValueAt(0.5, 1.0)
        self.center_glow_anim.setEndValue(0.0)
        self.center_glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.center_glow_anim.setLoopCount(-1)
        self.center_glow_anim.start()

        self.orbital_anim = QPropertyAnimation(self, b"orbital_angle")
        self.orbital_anim.setDuration(8000)
        self.orbital_anim.setStartValue(0.0)
        self.orbital_anim.setEndValue(360.0)
        self.orbital_anim.setEasingCurve(QEasingCurve.Type.Linear)
        self.orbital_anim.setLoopCount(-1)
        self.orbital_anim.start()

    def sizeHint(self):
        return QSize(280, 280)

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, val):
        self._progress = val
        self.update()

    @pyqtProperty(float)
    def glow_intensity(self):
        return self._glow_intensity

    @glow_intensity.setter
    def glow_intensity(self, val):
        self._glow_intensity = val
        self.update()

    @pyqtProperty(float)
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, val):
        self._rotation = val
        self.update()

    @pyqtProperty(float)
    def idle_rotation(self):
        return self._idle_rotation

    @idle_rotation.setter
    def idle_rotation(self, val):
        self._idle_rotation = val
        self.update()

    @pyqtProperty(float)
    def idle_glow(self):
        return self._idle_glow

    @idle_glow.setter
    def idle_glow(self, val):
        self._idle_glow = val
        self.update()

    @pyqtProperty(float)
    def ready_pulse(self):
        return self._ready_pulse

    @ready_pulse.setter
    def ready_pulse(self, val):
        self._ready_pulse = val
        self.update()

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, val):
        self._opacity = val
        self.update()

    @pyqtProperty(float)
    def center_glow(self):
        return self._center_glow

    @center_glow.setter
    def center_glow(self, val):
        self._center_glow = val
        self.update()

    @pyqtProperty(float)
    def orbital_angle(self):
        return self._orbital_angle

    @orbital_angle.setter
    def orbital_angle(self, val):
        self._orbital_angle = val
        self.update()

    def set_remaining(self, seconds: int):
        self._remaining = max(0, seconds)
        if self._total == 0:
            self._total = max(1, seconds)
        ratio = self._remaining / self._total if self._total else 0

        self.progress_anim.stop()
        self.progress_anim.setDuration(400)
        self.progress_anim.setStartValue(self._progress)
        self.progress_anim.setEndValue(ratio)
        self.progress_anim.start()

        if ratio < 0.1 and not self._warning_mode:
            self._warning_mode = True
            self.glow_anim.setLoopCount(-1)
            self.glow_anim.start()
            self.rotation_anim.start()

    def reset(self):
        self._warning_mode = False
        self._total = 1
        self._remaining = 0
        self.glow_anim.stop()
        self.rotation_anim.stop()
        self._glow_intensity = 0.0
        self._rotation = 0.0

        self.idle_rot_anim.start()
        self.idle_glow_anim.start()
        self.ready_pulse_anim.start()
        self.center_glow_anim.start()
        self.orbital_anim.start()

        self.progress_anim.stop()
        self.progress_anim.setDuration(600)
        self.progress_anim.setStartValue(self._progress)
        self.progress_anim.setEndValue(0.0)
        self.progress_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.progress_anim.start()
        self.update()

    def set_total(self, total: int):
        self._total = max(1, total)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setOpacity(self._opacity)

        side = min(self.width(), self.height())
        cx = self.width() / 2
        cy = self.height() / 2
        radius = side / 2 - 16

        outer = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        inner = outer.adjusted(6, 6, -6, -6)

        bg_grad = QRadialGradient(cx, cy, radius)
        bg_grad.setColorAt(0.0, QColor(COLORS["bg_1"]))
        bg_grad.setColorAt(0.6, QColor(COLORS["bg_1"]))
        bg_grad.setColorAt(0.85, QColor(COLORS["bg_2"]))
        bg_grad.setColorAt(1.0, QColor(COLORS["bg_3"]))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(bg_grad)
        p.drawEllipse(outer)

        center_alpha = int(15 * self._center_glow)
        if center_alpha > 0 and self._remaining <= 0:
            cg = QRadialGradient(cx, cy, radius * 0.5)
            cg.setColorAt(0.0, QColor(*_ACCENT_RGB, center_alpha))
            cg.setColorAt(0.5, QColor(*_ACCENT_RGB, center_alpha // 3))
            cg.setColorAt(1.0, QColor(*_ACCENT_RGB, 0))
            p.setBrush(cg)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(cx - radius * 0.5, cy - radius * 0.5, radius, radius))

        track_pen = QPen(QColor(COLORS["border_soft"]), 5)
        track_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(track_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(inner)

        shimmer = QConicalGradient(cx, cy, self._idle_rotation)
        shimmer.setColorAt(0.0, QColor(*_ACCENT_RGB, 0))
        shimmer.setColorAt(0.15, QColor(*_ACCENT_RGB, int(14 * self._idle_glow)))
        shimmer.setColorAt(0.3, QColor(*_ACCENT_RGB, 0))
        shimmer.setColorAt(0.5, QColor(*_ACCENT_RGB, 0))
        shimmer.setColorAt(0.65, QColor(*_ACCENT_RGB, int(10 * self._idle_glow)))
        shimmer.setColorAt(0.8, QColor(*_ACCENT_RGB, 0))
        shimmer_pen = QPen(shimmer, 3)
        shimmer_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(shimmer_pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(inner)

        idle_glow_alpha = int(15 * self._idle_glow)
        if idle_glow_alpha > 0:
            ring_color = QColor(*_ACCENT_RGB, idle_glow_alpha)
            for i in range(3, 0, -1):
                spread = i * 3
                glow_rect = inner.adjusted(-spread, -spread, spread, spread)
                c = QColor(ring_color.red(), ring_color.green(), ring_color.blue(),
                          int(ring_color.alpha() * (4 - i) / 3))
                pen = QPen(c, 1.5)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(glow_rect)

        if self._remaining <= 0:
            p.save()
            p.translate(cx, cy)
            p.rotate(self._orbital_angle)
            p.translate(-cx, -cy)
            for i in range(3):
                angle = math.radians(i * 120)
                dot_r = radius - 14
                dx = cx + dot_r * math.cos(angle)
                dy = cy + dot_r * math.sin(angle)
                dot_alpha = int(60 + 100 * self._idle_glow * (0.5 + 0.5 * math.sin(self._orbital_angle * 0.05 + i)))
                dot_color = QColor(*_ACCENT_RGB, dot_alpha)
                p.setBrush(dot_color)
                p.setPen(Qt.PenStyle.NoPen)
                p.drawEllipse(QRectF(dx - 2, dy - 2, 4, 4))
            p.restore()

        p.save()
        p.translate(cx, cy)
        p.rotate(self._idle_rotation * 0.3)
        p.translate(-cx, -cy)
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            is_major = i % 5 == 0
            r = radius + 10
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            size = 2.5 if is_major else 1.2
            if is_major:
                brightness = int(71 + 20 * self._idle_glow)
                p.setBrush(QColor(brightness, brightness, brightness + 20))
            else:
                p.setBrush(QColor(COLORS["border_soft"]))
            p.drawEllipse(QRectF(x - size, y - size, size * 2, size * 2))
        p.restore()

        if self._warning_mode and self._progress > 0:
            p.save()
            p.translate(cx, cy)
            p.rotate(self._rotation)
            p.translate(-cx, -cy)
            for i in range(4):
                angle = math.radians(i * 90)
                r = radius + 10
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                glow = QColor(COLORS["danger_1"])
                glow.setAlpha(int(80 * self._glow_intensity))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(glow)
                p.drawEllipse(QRectF(x - 4, y - 4, 8, 8))
            p.restore()

        if self._progress > 0:
            color = self._get_color_for_progress()

            glow_pen = QPen(QColor(color.red(), color.green(), color.blue(), 40), 20)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(glow_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            span = int(self._progress * 360 * 16)
            p.drawArc(inner, 90 * 16, -span)

            main_pen = QPen(color, 6)
            main_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(main_pen)
            p.drawArc(inner, 90 * 16, -span)

            tip_angle = math.radians(90 - self._progress * 360)
            tip_x = cx + (inner.width() / 2) * math.cos(tip_angle)
            tip_y = cy - (inner.height() / 2) * math.sin(tip_angle)

            dot_grad = QRadialGradient(tip_x, tip_y, 10)
            dot_grad.setColorAt(0.0, color)
            dot_grad.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 120))
            dot_grad.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 0))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(dot_grad)
            p.drawEllipse(QRectF(tip_x - 10, tip_y - 10, 20, 20))

            p.setBrush(color)
            p.drawEllipse(QRectF(tip_x - 3, tip_y - 3, 6, 6))

        if self._warning_mode:
            intensity = self._glow_intensity
            glow_color = QColor(COLORS["danger_1"])
            glow_color.setAlpha(int(30 * intensity))
            for i in range(3, 0, -1):
                spread = i * 6
                glow_rect = outer.adjusted(-spread, -spread, spread, spread)
                ring_color = QColor(glow_color.red(), glow_color.green(), glow_color.blue(),
                                   int(glow_color.alpha() * (4 - i) / 3))
                pen = QPen(ring_color, 2)
                p.setPen(pen)
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(glow_rect)

        hours = self._remaining // 3600
        minutes = (self._remaining % 3600) // 60
        seconds = self._remaining % 60

        if hours > 0:
            time_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"

        font = QFont("JetBrains Mono, Noto Sans Mono, DejaVu Sans Mono, monospace")
        font.setPixelSize(int(radius * 0.35))
        font.setWeight(QFont.Weight.ExtraBold)
        p.setFont(font)

        if self._warning_mode:
            alpha = int(180 + 75 * self._glow_intensity)
            warn = QColor(COLORS["danger_2"])
            warn.setAlpha(alpha)
            p.setPen(warn)
        else:
            p.setPen(QColor(COLORS["text_primary"]))

        time_rect = QRectF(outer.x(), outer.y() + outer.height() * 0.30,
                          outer.width(), outer.height() * 0.32)
        p.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, time_str)

        font2 = QFont("JetBrains Mono, Noto Sans Mono, DejaVu Sans Mono, monospace")
        font2.setPixelSize(int(radius * 0.1))
        font2.setWeight(QFont.Weight.DemiBold)
        p.setFont(font2)

        if self._remaining <= 0:
            label_alpha = int(80 + 175 * self._ready_pulse)
            p.setPen(QColor(*_ACCENT_RGB, label_alpha))
        elif self._warning_mode:
            p.setPen(QColor(COLORS["danger_1"]))
        else:
            p.setPen(QColor(COLORS["text_muted"]))

        label_rect = QRectF(outer.x(), outer.y() + outer.height() * 0.58,
                           outer.width(), outer.height() * 0.12)

        if self._remaining <= 0:
            text = "READY"
        elif self._warning_mode:
            text = "SHUTTING DOWN"
        else:
            text = "REMAINING"

        p.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, text)

        if self._remaining <= 0:
            bar_alpha = int(60 + 195 * self._ready_pulse)
            accent_pen = QPen(QColor(*_ACCENT_RGB, bar_alpha), 2)
            p.setPen(accent_pen)
            bar_y = cy + radius * 0.47
            bar_w = radius * 0.35
            p.drawLine(
                int(cx - bar_w / 2), int(bar_y),
                int(cx + bar_w / 2), int(bar_y)
            )

            dot_y = bar_y
            dot_x1 = cx - bar_w / 2
            dot_x2 = cx + bar_w / 2
            p.setBrush(QColor(*_ACCENT_RGB, bar_alpha))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(dot_x1 - 1.5, dot_y - 1.5, 3, 3))
            p.drawEllipse(QRectF(dot_x2 - 1.5, dot_y - 1.5, 3, 3))

        p.end()

    def _get_color_for_progress(self) -> QColor:
        if self._progress > 0.5:
            return QColor(COLORS["success_1"])
        elif self._progress > 0.2:
            return QColor(COLORS["warning"])
        else:
            return QColor(COLORS["danger_1"])
