DARK_THEME = """
* {
    margin: 0;
    padding: 0;
    outline: none;
}

QWidget {
    background-color: transparent;
    color: #e2e8f0;
    font-family: "Cantarell", "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 10pt;
}

QMainWindow {
    background-color: transparent;
}

/* ── Generic Buttons ─────────────────────────────────── */

QPushButton {
    background-color: #1e293b;
    color: #94a3b8;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 7px 18px;
    font-weight: 600;
    font-size: 9.5pt;
}

QPushButton:hover {
    background-color: #2d3a4e;
    color: #e2e8f0;
    border: 1px solid #475569;
}

QPushButton:pressed {
    background-color: #1f2937;
    color: #cbd5e1;
}

QPushButton:disabled {
    background-color: #111827;
    color: #475569;
    border: 1px solid #1e293b;
}

/* ── Primary action (Start timer) ────────────────────── */

QPushButton#start-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #059669, stop:0.5 #10b981, stop:1 #34d399);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 10px 36px;
    font-size: 11pt;
    font-weight: 700;
    min-width: 140px;
}

QPushButton#start-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #10b981, stop:0.5 #34d399, stop:1 #6ee7b7);
}

QPushButton#start-btn:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #047857, stop:0.5 #059669, stop:1 #10b981);
}

/* ── Destructive action (Cancel) ─────────────────────── */

QPushButton#cancel-btn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #dc2626, stop:0.5 #ef4444, stop:1 #f87171);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 10px 36px;
    font-size: 11pt;
    font-weight: 700;
    min-width: 140px;
}

QPushButton#cancel-btn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ef4444, stop:0.5 #f87171, stop:1 #fca5a5);
}

/* ── Preset time buttons ─────────────────────────────── */

QPushButton#preset-btn {
    background-color: #1e293b;
    color: #64748b;
    border: 1px solid #2d3a4e;
    border-radius: 14px;
    padding: 4px 12px;
    font-family: "Noto Sans Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 9pt;
    font-weight: 600;
    min-width: 44px;
    min-height: 22px;
}

QPushButton#preset-btn:hover {
    background-color: #2d3a4e;
    color: #94a3b8;
    border: 1px solid #3b82f6;
}

QPushButton#preset-btn:pressed {
    background-color: #1f2937;
    color: #3b82f6;
}

/* ── Mode selector (pill tabs) ───────────────────────── */

QPushButton#mode-countdown, QPushButton#mode-schedule {
    background-color: #1e293b;
    color: #64748b;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 6px 20px;
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    min-height: 28px;
}

QPushButton#mode-countdown:checked, QPushButton#mode-schedule:checked {
    background-color: #1d4ed8;
    color: #ffffff;
    border: 1px solid #2563eb;
}

QPushButton#mode-countdown:hover, QPushButton#mode-schedule:hover {
    color: #94a3b8;
    border: 1px solid #475569;
}

QPushButton#mode-countdown:checked:hover, QPushButton#mode-schedule:checked:hover {
    background-color: #2563eb;
    color: #ffffff;
}

QPushButton#mode-countdown:focus, QPushButton#mode-schedule:focus {
    border: 1px solid #334155;
}

/* ── Spin boxes / Time edit ──────────────────────────── */

QSpinBox, QTimeEdit {
    background-color: #1e293b;
    color: #f1f5f9;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 8px 14px;
    font-family: "Noto Sans Mono", "DejaVu Sans Mono", "Liberation Mono", monospace;
    font-size: 14pt;
    font-weight: 700;
    min-width: 70px;
    min-height: 24px;
    selection-background-color: #3b82f6;
}

QSpinBox:focus, QTimeEdit:focus {
    border: 1px solid #3b82f6;
    background-color: #1a2335;
}

QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {
    background-color: #2d3a4e;
    border: none;
    border-radius: 4px;
    width: 18px;
    margin: 3px 2px;
    subcontrol-origin: padding;
}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
    background-color: #3b82f6;
}

QSpinBox::up-button:pressed, QSpinBox::down-button:pressed,
QTimeEdit::up-button:pressed, QTimeEdit::down-button:pressed {
    background-color: #2563eb;
}

QSpinBox::up-arrow, QTimeEdit::up-arrow {
    width: 8px;
    height: 8px;
}

QSpinBox::down-arrow, QTimeEdit::down-arrow {
    width: 8px;
    height: 8px;
}

/* ── Labels ──────────────────────────────────────────── */

QLabel {
    color: #e2e8f0;
    background: transparent;
}

QLabel#title-label {
    color: #64748b;
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}

QLabel#status-label {
    font-size: 9pt;
    color: #94a3b8;
    font-weight: 500;
}

QLabel#separator {
    color: #475569;
    font-size: 18pt;
    font-weight: 300;
}

/* ── Containers ──────────────────────────────────────── */

QFrame#main-container {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #141d2b, stop:0.4 #111827, stop:0.7 #0f172a, stop:1 #0d1520);
    border: 1px solid #1e293b;
    border-radius: 20px;
}

/* ── Scrollbar ───────────────────────────────────────── */

QScrollBar:vertical {
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
