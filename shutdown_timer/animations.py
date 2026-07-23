from PyQt6.QtCore import (
    QPropertyAnimation,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QPauseAnimation,
    QEasingCurve,
    QPoint,
    QRect,
    pyqtProperty,
)
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget


def fade_in(widget: QWidget, duration: int = 400, delay: int = 0) -> QPropertyAnimation:
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    if delay:
        group = QSequentialAnimationGroup()
        group.addAnimation(QPauseAnimation(delay))
        group.addAnimation(anim)
        group.start()
        return group
    anim.start()
    return anim


def fade_out(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.Type.InCubic)
    anim.start()
    return anim


def slide_in_from_bottom(widget: QWidget, duration: int = 500, distance: int = 60) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    geo = widget.geometry()
    anim.setStartValue(QRect(geo.x(), geo.y() + distance, geo.width(), geo.height()))
    anim.setEndValue(geo)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim


def slide_in_from_right(widget: QWidget, duration: int = 400, distance: int = 80) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    geo = widget.geometry()
    anim.setStartValue(QRect(geo.x() + distance, geo.y(), geo.width(), geo.height()))
    anim.setEndValue(geo)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim


def slide_in_from_left(widget: QWidget, duration: int = 400, distance: int = 80) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    geo = widget.geometry()
    anim.setStartValue(QRect(geo.x() - distance, geo.y(), geo.width(), geo.height()))
    anim.setEndValue(geo)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim


def bounce_in(widget: QWidget, duration: int = 600) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    geo = widget.geometry()
    anim.setStartValue(geo)
    anim.setKeyValueAt(0.4, QRect(geo.x() - 4, geo.y() - 4, geo.width() + 8, geo.height() + 8))
    anim.setKeyValueAt(0.7, QRect(geo.x() + 2, geo.y() + 2, geo.width() - 4, geo.height() - 4))
    anim.setEndValue(geo)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    return anim


def pulse_glow(widget: QWidget, duration: int = 1200) -> QPropertyAnimation:
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setKeyValueAt(0.0, 0.6)
    anim.setKeyValueAt(0.5, 1.0)
    anim.setKeyValueAt(1.0, 0.6)
    anim.setEasingCurve(QEasingCurve.Type.InOutSine)
    anim.setLoopCount(-1)
    anim.start()
    return anim


def shake_window(window: QWidget, duration: int = 500) -> QSequentialAnimationGroup:
    group = QSequentialAnimationGroup()
    geo = window.geometry()
    shake_offsets = [8, -8, 6, -6, 4, -4, 2, -2, 0]

    for offset in shake_offsets:
        anim = QPropertyAnimation(window, b"geometry")
        anim.setDuration(duration // len(shake_offsets))
        anim.setEndValue(QRect(geo.x() + offset, geo.y(), geo.width(), geo.height()))
        anim.setEasingCurve(QEasingCurve.Type.Linear)
        group.addAnimation(anim)

    group.start()
    return group


def scale_up(widget: QWidget, duration: int = 300) -> QPropertyAnimation:
    anim = QPropertyAnimation(widget, b"geometry")
    anim.setDuration(duration)
    geo = widget.geometry()
    cx, cy = geo.center().x(), geo.center().y()
    w, h = geo.width(), geo.height()
    anim.setStartValue(QRect(cx - w // 2, cy - h // 2, 0, 0))
    anim.setEndValue(geo)
    anim.setEasingCurve(QEasingCurve.Type.OutBack)
    anim.start()
    return anim
