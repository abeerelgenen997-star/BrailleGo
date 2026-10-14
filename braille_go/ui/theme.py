"""الثيم والخطوط والألوان.

``apply_theme`` reads the learner's preferences (font size, theme, high
contrast, custom colours) and applies them to the whole application: it sets a
font family that covers Arabic, a :class:`QPalette` (so native Qt widgets such
as dialogs and combo boxes follow the theme as well) and a stylesheet for the
custom-drawn parts.

Only the *application's* appearance is touched.  Nothing here changes Windows
or screen-reader settings, as required by the accessibility brief.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

#: حجم الخط الأساسي بالنقاط قبل تطبيق تكبير المستخدم.
BASE_FONT_POINT_SIZE = 11.0

#: خطوط مرشّحة تدعم العربية على Windows ثم الخطوط المفتوحة الشائعة.
FONT_CANDIDATES = (
    "Segoe UI",
    "Tahoma",
    "Arabic Typesetting",
    "Noto Sans Arabic",
    "DejaVu Sans",
    "Arial",
)

#: خطوط تُعرف باحتوائها على محارف برايل في يونيكود.
BRAILLE_FONT_CANDIDATES = (
    "Segoe UI Symbol",
    "Segoe UI",
    "Noto Sans Symbols 2",
    "DejaVu Sans",
)


@dataclass(frozen=True)
class ThemeColors:
    """ألوان الواجهة المستخدمة في التنسيق والرسم."""

    background: str
    surface: str
    surface_alt: str
    text: str
    muted_text: str
    accent: str
    accent_text: str
    border: str
    focus: str
    success: str
    error: str
    dot_on: str
    dot_off: str
    dot_border: str


_LIGHT = ThemeColors(
    background="#f4f6f8",
    surface="#ffffff",
    surface_alt="#eaeef3",
    text="#111418",
    muted_text="#4a525c",
    accent="#0b5fa5",
    accent_text="#ffffff",
    border="#c3ccd6",
    focus="#ff8c00",
    success="#0a7d3c",
    error="#a11212",
    dot_on="#111418",
    dot_off="#d8dee5",
    dot_border="#5a636d",
)

_DARK = ThemeColors(
    background="#12151a",
    surface="#1c2128",
    surface_alt="#252b34",
    text="#f2f5f8",
    muted_text="#c2cad3",
    accent="#5aa9e6",
    accent_text="#08131c",
    border="#3a424d",
    focus="#ffb454",
    success="#5ddb92",
    error="#ff8080",
    dot_on="#f2f5f8",
    dot_off="#39414b",
    dot_border="#8892a0",
)

_HIGH_CONTRAST_LIGHT = ThemeColors(
    background="#ffffff",
    surface="#ffffff",
    surface_alt="#f0f0f0",
    text="#000000",
    muted_text="#000000",
    accent="#00007a",
    accent_text="#ffffff",
    border="#000000",
    focus="#c00000",
    success="#005000",
    error="#a00000",
    dot_on="#000000",
    dot_off="#ffffff",
    dot_border="#000000",
)

_HIGH_CONTRAST_DARK = ThemeColors(
    background="#000000",
    surface="#000000",
    surface_alt="#101010",
    text="#ffffff",
    muted_text="#ffffff",
    accent="#ffff00",
    accent_text="#000000",
    border="#ffffff",
    focus="#00ffff",
    success="#00ff6a",
    error="#ff6b6b",
    dot_on="#ffffff",
    dot_off="#000000",
    dot_border="#ffffff",
)


def theme_colors(settings) -> ThemeColors:
    """أعد الألوان المناسبة للإعدادات الحالية."""
    high_contrast = bool(settings.get("high_contrast", False))
    dark = settings.get("theme", "light") == "dark"
    if high_contrast:
        base = _HIGH_CONTRAST_DARK if dark else _HIGH_CONTRAST_LIGHT
    else:
        base = _DARK if dark else _LIGHT

    text_override = str(settings.get("text_color", "") or "").strip()
    bg_override = str(settings.get("background_color", "") or "").strip()
    dot_on = str(settings.get("dot_color", "") or "").strip() or base.dot_on
    dot_off = str(settings.get("dot_empty_color", "") or "").strip() or base.dot_off
    dot_border = str(settings.get("dot_border_color", "") or "").strip() or base.dot_border

    return ThemeColors(
        background=bg_override or base.background,
        surface=base.surface,
        surface_alt=base.surface_alt,
        text=text_override or base.text,
        muted_text=base.muted_text,
        accent=base.accent,
        accent_text=base.accent_text,
        border=base.border,
        focus=base.focus,
        success=base.success,
        error=base.error,
        dot_on=dot_on,
        dot_off=dot_off,
        dot_border=dot_border,
    )


def pick_font(point_size: float | None = None) -> QFont:
    """خط أساسي يدعم العربية بحجم مناسب."""
    font = QFont()
    font.setFamilies(list(FONT_CANDIDATES))
    font.setPointSizeF(point_size or BASE_FONT_POINT_SIZE)
    font.setStyleStrategy(QFont.PreferAntialias)
    return font


def braille_font(point_size: float) -> QFont:
    """خط لعرض محارف برايل في يونيكود (تمثيل ثانوي إلى جانب الرسم)."""
    font = QFont()
    font.setFamilies(list(BRAILLE_FONT_CANDIDATES))
    font.setPointSizeF(point_size)
    return font


def scaled_point_size(settings) -> float:
    """حجم الخط الفعلي بعد تطبيق تكبير المستخدم."""
    try:
        scale = float(settings.get("font_scale", 1.0))
    except (TypeError, ValueError):
        scale = 1.0
    return max(8.0, min(40.0, BASE_FONT_POINT_SIZE * scale))


def build_palette(colors: ThemeColors) -> QPalette:
    """لوحة ألوان لتطبيقها على التطبيق كاملًا."""
    palette = QPalette()
    background = QColor(colors.background)
    surface = QColor(colors.surface)
    text = QColor(colors.text)
    accent = QColor(colors.accent)

    palette.setColor(QPalette.Window, background)
    palette.setColor(QPalette.WindowText, text)
    palette.setColor(QPalette.Base, surface)
    palette.setColor(QPalette.AlternateBase, QColor(colors.surface_alt))
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.Button, surface)
    palette.setColor(QPalette.ButtonText, text)
    palette.setColor(QPalette.Highlight, accent)
    palette.setColor(QPalette.HighlightedText, QColor(colors.accent_text))
    palette.setColor(QPalette.ToolTipBase, surface)
    palette.setColor(QPalette.ToolTipText, text)
    palette.setColor(QPalette.PlaceholderText, QColor(colors.muted_text))
    palette.setColor(QPalette.Link, accent)
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(colors.muted_text))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(colors.muted_text))
    return palette


def build_stylesheet(colors: ThemeColors) -> str:
    """ورقة تنسيق للعناصر المخصّصة."""
    return f"""
    QWidget {{
        color: {colors.text};
    }}
    QMainWindow, QDialog {{
        background-color: {colors.background};
    }}
    QLabel#screenTitle {{
        font-size: 1.6em;
        font-weight: bold;
        padding: 6px 2px;
    }}
    QLabel#cardHeading {{
        font-size: 1.15em;
        font-weight: bold;
        padding-bottom: 4px;
    }}
    QLabel#muted {{
        color: {colors.muted_text};
    }}
    QFrame#card {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: 8px;
    }}
    QFrame#headerBar {{
        background-color: {colors.surface_alt};
        border-bottom: 1px solid {colors.border};
    }}
    QLabel#feedbackOk {{
        color: {colors.success};
        font-weight: bold;
        font-size: 1.1em;
    }}
    QLabel#feedbackError {{
        color: {colors.error};
        font-weight: bold;
        font-size: 1.1em;
    }}
    QLabel#statusBanner {{
        background-color: {colors.surface_alt};
        border: 1px solid {colors.border};
        border-radius: 6px;
        padding: 6px;
    }}
    QPushButton {{
        background-color: {colors.surface};
        border: 2px solid {colors.border};
        border-radius: 8px;
        padding: 9px 14px;
        min-height: 24px;
        text-align: center;
    }}
    QPushButton:hover:enabled {{
        border-color: {colors.accent};
    }}
    QPushButton:focus {{
        border: 3px solid {colors.focus};
    }}
    QPushButton:disabled {{
        color: {colors.muted_text};
        border-style: dashed;
    }}
    QPushButton[primary="true"] {{
        background-color: {colors.accent};
        color: {colors.accent_text};
        border-color: {colors.accent};
        font-weight: bold;
    }}
    QPushButton[primary="true"]:focus {{
        border: 3px solid {colors.focus};
    }}
    QPushButton[danger="true"] {{
        color: {colors.error};
        border-color: {colors.error};
    }}
    QPushButton#choice:checked {{
        border: 3px solid {colors.accent};
        background-color: {colors.surface_alt};
    }}
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QPlainTextEdit {{
        background-color: {colors.surface};
        border: 2px solid {colors.border};
        border-radius: 6px;
        padding: 6px;
        min-height: 24px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {colors.focus};
    }}
    QProgressBar {{
        border: 2px solid {colors.border};
        border-radius: 6px;
        text-align: center;
        min-height: 22px;
        background-color: {colors.surface};
    }}
    QProgressBar::chunk {{
        background-color: {colors.accent};
    }}
    QListWidget, QTableWidget {{
        background-color: {colors.surface};
        border: 1px solid {colors.border};
        border-radius: 6px;
    }}
    QListWidget::item:selected, QTableWidget::item:selected {{
        background-color: {colors.accent};
        color: {colors.accent_text};
    }}
    QScrollArea {{
        border: none;
    }}
    QGroupBox {{
        border: 1px solid {colors.border};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 10px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 4px;
    }}
    """


def apply_theme(app: QApplication, settings) -> None:
    """طبّق الثيم والخط على التطبيق بأكمله."""
    colors = theme_colors(settings)
    app.setPalette(build_palette(colors))
    app.setFont(pick_font(scaled_point_size(settings)))
    app.setStyleSheet(build_stylesheet(colors))
    app.setProperty("brailleGoColors", {
        "dot_on": colors.dot_on,
        "dot_off": colors.dot_off,
        "dot_border": colors.dot_border,
        "focus": colors.focus,
        "accent": colors.accent,
        "text": colors.text,
    })
