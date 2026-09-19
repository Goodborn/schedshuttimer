# ── Design tokens ────────────────────────────────────────────
# Shared palette used both by the QSS below and by the custom-painted
# widgets (circular_timer, shimmer_button, ambient_background, title_bar)
# so everything renders from one source of truth.

COLORS = {
    "bg_0": "#080b13",
    "bg_1": "#0d1220",
    "bg_2": "#121a2c",
    "bg_3": "#1a2440",
    "surface": "#141b2e",
    "surface_alt": "#1b2438",
    "border": "#26314d",
    "border_soft": "#1c2540",

    "text_primary": "#f1f5f9",
    "text_secondary": "#9aa7c2",
    "text_muted": "#5c6a8c",

    "accent_0": "#6366f1",
    "accent_1": "#818cf8",
    "accent_2": "#a78bfa",
    "cyan": "#22d3ee",

    "success_0": "#059669",
    "success_1": "#10b981",
    "success_2": "#34d399",

    "danger_0": "#e11d48",
    "danger_1": "#f43f5e",
    "danger_2": "#fb7185",

    "warning": "#f59e0b",
}

DARK_THEME = f"""
* {{
    margin: 0;
    padding: 0;
    outline: none;
}}

QWidget {{
    background-color: transparent;
    color: {COLORS["text_primary"]};
    font-family: "Inter", "Cantarell", "DejaVu Sans", "Noto Sans", sans-serif;
    font-size: 10pt;
}}

QMainWindow {{
    background-color: transparent;
}}

QToolTip {{
    background-color: {COLORS["surface_alt"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    padding: 4px 8px;
}}

/* ── Generic Buttons ─────────────────────────────────── */

QPushButton {{
    background-color: {COLORS["surface_alt"]};
    color: {COLORS["text_secondary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 7px 18px;
    font-weight: 600;
    font-size: 9.5pt;
}}

QPushButton:hover {{
    background-color: #232f4d;
    color: {COLORS["text_primary"]};
    border: 1px solid #3a4a72;
}}

QPushButton:pressed {{
    background-color: #161e33;
    color: {COLORS["text_secondary"]};
}}

QPushButton:disabled {{
    background-color: {COLORS["bg_1"]};
    color: {COLORS["text_muted"]};
    border: 1px solid {COLORS["border_soft"]};
}}

/* ── Preset time buttons ─────────────────────────────── */

QPushButton#preset-btn {{
    background-color: {COLORS["surface_alt"]};
    color: {COLORS["text_muted"]};
    border: 1px solid {COLORS["border_soft"]};
    border-radius: 14px;
    padding: 4px 12px;
    font-family: "JetBrains Mono", "Noto Sans Mono", "DejaVu Sans Mono", monospace;
    font-size: 9pt;
    font-weight: 600;
    min-width: 44px;
    min-height: 22px;
}}

QPushButton#preset-btn:hover {{
    background-color: #232f4d;
    color: {COLORS["text_secondary"]};
    border: 1px solid {COLORS["accent_0"]};
}}

QPushButton#preset-btn:pressed {{
    background-color: #161e33;
    color: {COLORS["accent_1"]};
}}

/* ── Mode selector (pill tabs) ───────────────────────── */

QPushButton#mode-countdown, QPushButton#mode-schedule, QPushButton#mode-idle {{
    background-color: transparent;
    color: {COLORS["text_muted"]};
    border: none;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 9pt;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    min-height: 28px;
}}

QPushButton#mode-countdown:checked, QPushButton#mode-schedule:checked, QPushButton#mode-idle:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS["accent_0"]}, stop:1 {COLORS["accent_2"]});
    color: #ffffff;
}}

QPushButton#mode-countdown:hover:!checked, QPushButton#mode-schedule:hover:!checked, QPushButton#mode-idle:hover:!checked {{
    color: {COLORS["text_secondary"]};
    background-color: {COLORS["border_soft"]};
}}

/* ── Spin boxes / Time edit ──────────────────────────── */

QSpinBox, QTimeEdit {{
    background-color: {COLORS["surface_alt"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    padding: 8px 14px;
    font-family: "JetBrains Mono", "Noto Sans Mono", "DejaVu Sans Mono", monospace;
    font-size: 14pt;
    font-weight: 700;
    min-width: 70px;
    min-height: 24px;
    selection-background-color: {COLORS["accent_0"]};
}}

QSpinBox:hover, QTimeEdit:hover {{
    border: 1px solid #3a4a72;
}}

QSpinBox:focus, QTimeEdit:focus {{
    border: 1px solid {COLORS["accent_1"]};
    background-color: #17203a;
}}

QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button {{
    background-color: {COLORS["border_soft"]};
    border: none;
    border-radius: 4px;
    width: 18px;
    margin: 3px 2px;
    subcontrol-origin: padding;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
    background-color: {COLORS["accent_0"]};
}}

QSpinBox::up-button:pressed, QSpinBox::down-button:pressed,
QTimeEdit::up-button:pressed, QTimeEdit::down-button:pressed {{
    background-color: {COLORS["accent_1"]};
}}

QSpinBox::up-arrow, QTimeEdit::up-arrow {{
    width: 8px;
    height: 8px;
}}

QSpinBox::down-arrow, QTimeEdit::down-arrow {{
    width: 8px;
    height: 8px;
}}

/* ── Labels ──────────────────────────────────────────── */

QLabel {{
    color: {COLORS["text_primary"]};
    background: transparent;
}}

QLabel#title-label {{
    color: {COLORS["text_muted"]};
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
}}

QLabel#status-label {{
    font-size: 9pt;
    color: {COLORS["text_secondary"]};
    font-weight: 500;
}}

QLabel#separator {{
    color: {COLORS["text_muted"]};
    font-size: 18pt;
    font-weight: 300;
}}

QLabel#brand-label {{
    color: {COLORS["text_secondary"]};
    font-size: 8pt;
    font-weight: 700;
    letter-spacing: 2px;
}}

/* ── Containers ──────────────────────────────────────── */

QFrame#main-container {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {COLORS["bg_3"]}, stop:0.35 {COLORS["bg_2"]},
        stop:0.7 {COLORS["bg_1"]}, stop:1 {COLORS["bg_0"]});
    border: 1px solid {COLORS["border_soft"]};
    border-radius: 22px;
}}

QFrame#title-bar {{
    background: transparent;
    border-top-left-radius: 22px;
    border-top-right-radius: 22px;
}}

/* ── Message boxes (quit / confirm dialogs) ──────────── */

QMessageBox {{
    background-color: {COLORS["bg_1"]};
}}

QMessageBox QLabel {{
    color: {COLORS["text_primary"]};
    font-size: 10pt;
}}

QMessageBox QPushButton {{
    min-width: 80px;
    padding: 6px 16px;
}}

/* ── Scrollbar ───────────────────────────────────────── */

QScrollBar:vertical {{
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS["border"]};
    border-radius: 3px;
    min-height: 20px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
