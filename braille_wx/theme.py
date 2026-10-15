"""الثيم وأنماط العرض المتنوّعة لنسخة wxPython.

يوفّر هذا الملف **أنماط عرض جاهزة** تناسب مختلف أنواع الإعاقة البصرية
(تباين عالٍ، ضعف بصر شديد، طباعة كبيرة، عسر القراءة، عمى الألوان، رمادي)،
ويُسقِطها على كل عناصر التطبيق. كل الأنماط معرّفة هنا في مكان واحد حتى تكون
قابلة للاختبار والتوسّع بسهولة.
"""

from __future__ import annotations

from dataclasses import dataclass

import wx

#: خطوط مرشّحة تدعم العربية على Windows ثم البدائل المفتوحة.
FONT_CANDIDATES = (
    "Segoe UI",
    "Tahoma",
    "Arial",
)

#: خطوط تُعرف باحتوائها على محارف برايل في يونيكود.
BRAILLE_FONT_CANDIDATES = (
    "Segoe UI Symbol",
    "Segoe UI",
    "Arial",
)

#: حجم الخط الأساسي بالنقاط.
BASE_FONT_POINT_SIZE = 11.0


@dataclass(frozen=True)
class DisplayMode:
    """نمط عرض جاهز."""

    key: str
    label_key: str
    background: str
    surface: str
    surface_alt: str
    text: str
    muted: str
    accent: str
    accent_text: str
    border: str
    focus: str
    success: str
    error: str
    dot_on: str
    dot_off: str
    dot_border: str
    font_scale: float = 1.0
    bold: bool = False
    description_key: str = "display_mode_desc"


#: الأنماط الجاهزة المتاحة للمستخدم.
MODES: dict[str, DisplayMode] = {
    "normal_light": DisplayMode(
        "normal_light", "mode_normal_light",
        background="#f4f6f8", surface="#ffffff", surface_alt="#eaeef3",
        text="#111418", muted="#4a525c", accent="#0b5fa5", accent_text="#ffffff",
        border="#c3ccd6", focus="#ff8c00", success="#0a7d3c", error="#a11212",
        dot_on="#111418", dot_off="#d8dee5", dot_border="#5a636d",
    ),
    "normal_dark": DisplayMode(
        "normal_dark", "mode_normal_dark",
        background="#12151a", surface="#1c2128", surface_alt="#252b34",
        text="#f2f5f8", muted="#c2cad3", accent="#5aa9e6", accent_text="#08131c",
        border="#3a424d", focus="#ffb454", success="#5ddb92", error="#ff8080",
        dot_on="#f2f5f8", dot_off="#39414b", dot_border="#8892a0",
    ),
    "hc_light": DisplayMode(
        "hc_light", "mode_hc_light",
        background="#ffffff", surface="#ffffff", surface_alt="#f0f0f0",
        text="#000000", muted="#000000", accent="#00007a", accent_text="#ffffff",
        border="#000000", focus="#c00000", success="#005000", error="#a00000",
        dot_on="#000000", dot_off="#ffffff", dot_border="#000000",
        bold=True,
    ),
    "hc_dark": DisplayMode(
        "hc_dark", "mode_hc_dark",
        background="#000000", surface="#000000", surface_alt="#101010",
        text="#ffff00", muted="#ffff00", accent="#ffff00", accent_text="#000000",
        border="#ffff00", focus="#00ffff", success="#00ff6a", error="#ff6b6b",
        dot_on="#ffff00", dot_off="#000000", dot_border="#ffff00",
        bold=True,
    ),
    "yellow_black": DisplayMode(
        "yellow_black", "mode_yellow_black",
        background="#000000", surface="#0a0a0a", surface_alt="#141400",
        text="#ffee00", muted="#e0d000", accent="#ffee00", accent_text="#000000",
        border="#ffee00", focus="#00ffff", success="#66ff66", error="#ff6666",
        dot_on="#ffee00", dot_off="#2a2a00", dot_border="#ffee00",
        font_scale=1.4, bold=True,
    ),
    "large_print": DisplayMode(
        "large_print", "mode_large_print",
        background="#ffffff", surface="#ffffff", surface_alt="#eef2f6",
        text="#000000", muted="#333333", accent="#003366", accent_text="#ffffff",
        border="#333333", focus="#cc6600", success="#006600", error="#990000",
        dot_on="#000000", dot_off="#dddddd", dot_border="#444444",
        font_scale=1.7, bold=False,
    ),
    "low_vision": DisplayMode(
        "low_vision", "mode_low_vision",
        background="#fdf6e3", surface="#fffaf0", surface_alt="#f5ecd6",
        text="#1a1a1a", muted="#3a3a3a", accent="#7a4a00", accent_text="#ffffff",
        border="#b8a878", focus="#d2691e", success="#0a6b2a", error="#a11212",
        dot_on="#1a1a1a", dot_off="#e4d9b8", dot_border="#7a6a3a",
        font_scale=1.25,
    ),
    "deuteranopia": DisplayMode(
        "deuteranopia", "mode_deuteranopia",
        # لوحة Okabe–Ito الصديقة لعمى الألوان: أزرق/برتقالي/رمادي.
        background="#ffffff", surface="#ffffff", surface_alt="#eef1f5",
        text="#000000", muted="#3a3a3a", accent="#0072b2", accent_text="#ffffff",
        border="#0072b2", focus="#e69f00", success="#009e73", error="#d55e00",
        dot_on="#000000", dot_off="#d9d9d9", dot_border="#0072b2",
    ),
    "grayscale": DisplayMode(
        "grayscale", "mode_grayscale",
        background="#ffffff", surface="#ffffff", surface_alt="#ededed",
        text="#000000", muted="#3a3a3a", accent="#333333", accent_text="#ffffff",
        border="#666666", focus="#000000", success="#333333", error="#111111",
        dot_on="#000000", dot_off="#cccccc", dot_border="#666666",
    ),
    # --- أنماط إضافية لفئات أخرى من المستخدمين -------------------------
    "dyslexia": DisplayMode(
        "dyslexia", "mode_dyslexia",
        # خلفية كريمية دافئة تقلّل الوهج وتُريح القراءة لعُسر القراءة.
        background="#fbf0d9", surface="#fff8e7", surface_alt="#f3e6c8",
        text="#1b1b1b", muted="#3f3a2e", accent="#8a4b00", accent_text="#ffffff",
        border="#b59a5e", focus="#d2691e", success="#0a6b2a", error="#a11212",
        dot_on="#1b1b1b", dot_off="#e3d3a6", dot_border="#6b5a2e",
        font_scale=1.35,
    ),
    "protanopia": DisplayMode(
        "protanopia", "mode_protanopia",
        # لوحة Okabe–Ito (أزرق/أصفر) مناسبة لمن لا يميّز الأحمر.
        background="#ffffff", surface="#ffffff", surface_alt="#eef2f7",
        text="#000000", muted="#3a3a3a", accent="#0072b2", accent_text="#ffffff",
        border="#0072b2", focus="#f0e442", success="#009e73", error="#d55e00",
        dot_on="#000000", dot_off="#d9d9d9", dot_border="#0072b2",
    ),
    "tritanopia": DisplayMode(
        "tritanopia", "mode_tritanopia",
        # بديل بألوان وردية/فيروزية لمن لا يميّز الأزرق.
        background="#ffffff", surface="#ffffff", surface_alt="#f7eef2",
        text="#000000", muted="#3a3a3a", accent="#cc79a7", accent_text="#ffffff",
        border="#cc79a7", focus="#009e73", success="#0072b2", error="#d55e00",
        dot_on="#000000", dot_off="#dcd0d8", dot_border="#cc79a7",
    ),
    "sepia": DisplayMode(
        "sepia", "mode_sepia",
        # خلفية سيبيا مريحة للعين تقلّل الإجهاد عند القراءة الطويلة.
        background="#f4ecd8", surface="#faf3e0", surface_alt="#ece0c6",
        text="#3b2f1e", muted="#5c4b34", accent="#8a5a00", accent_text="#ffffff",
        border="#c0a878", focus="#a05a00", success="#3f6b2a", error="#8a2020",
        dot_on="#3b2f1e", dot_off="#ddcfa8", dot_border="#7a6440",
        font_scale=1.15,
    ),
    "oled_black": DisplayMode(
        "oled_black", "mode_oled",
        # أسود نقي مناسب لشاشات OLED وحساسية الضوء.
        background="#000000", surface="#0a0a0a", surface_alt="#141414",
        text="#ffffff", muted="#c8c8c8", accent="#4ea1ff", accent_text="#000000",
        border="#4a4a4a", focus="#ffd24d", success="#5ddb92", error="#ff8080",
        dot_on="#ffffff", dot_off="#2a2a2a", dot_border="#8a8a8a",
    ),
    "soft_pastel": DisplayMode(
        "soft_pastel", "mode_soft_pastel",
        # ألوان هادئة منخفضة الإثارة (مناسبة لفرط الحساسية الحسّية).
        background="#eef3f7", surface="#f7fbfd", surface_alt="#e2ebf2",
        text="#22303c", muted="#46586a", accent="#4a7a9b", accent_text="#ffffff",
        border="#a9bfd0", focus="#d08a3a", success="#3f7d5a", error="#a2565a",
        dot_on="#22303c", dot_off="#cfdde8", dot_border="#7f95a8",
    ),
    "senior": DisplayMode(
        "senior", "mode_senior",
        # خط كبير وتباين مرتفع لكبار السن والمبتدئين.
        background="#ffffff", surface="#ffffff", surface_alt="#f2f2f2",
        text="#000000", muted="#000000", accent="#003366", accent_text="#ffffff",
        border="#000000", focus="#b30000", success="#006400", error="#990000",
        dot_on="#000000", dot_off="#dddddd", dot_border="#222222",
        font_scale=2.0, bold=True,
    ),
}



def mode_choices() -> list[tuple[str, str]]:
    """قائمة (المفتاح، التسمية العربية) لبناء واجهة الإعدادات."""
    from . import i18n

    return [(key, i18n.t(mode.label_key)) for key, mode in MODES.items()]


def to_colour(value: str) -> wx.Colour:
    """حوّل لونًا نصيًا مثل ``#112233`` إلى ``wx.Colour``."""
    text = (value or "").strip().lstrip("#")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6:
        return wx.Colour(0, 0, 0)
    try:
        return wx.Colour(int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16))
    except ValueError:
        return wx.Colour(0, 0, 0)


class Theme:
    """يحسب الألوان والخط الفعلي من الإعدادات."""

    def __init__(self, settings) -> None:
        self.settings = settings
        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        key = str(self.settings.get("display_mode", "normal_light"))
        mode = MODES.get(key, MODES["normal_light"])
        self.mode = mode

        text_override = str(self.settings.get("text_color", "") or "").strip()
        bg_override = str(self.settings.get("background_color", "") or "").strip()
        dot_on = str(self.settings.get("dot_color", "") or "").strip() or mode.dot_on
        dot_off = str(self.settings.get("dot_empty_color", "") or "").strip() or mode.dot_off
        dot_border = str(self.settings.get("dot_border_color", "") or "").strip() or mode.dot_border

        self.colors: dict[str, str] = {
            "background": bg_override or mode.background,
            "surface": mode.surface,
            "surface_alt": mode.surface_alt,
            "text": text_override or mode.text,
            "muted": mode.muted,
            "accent": mode.accent,
            "accent_text": mode.accent_text,
            "border": mode.border,
            "focus": mode.focus,
            "success": mode.success,
            "error": mode.error,
            "dot_on": dot_on,
            "dot_off": dot_off,
            "dot_border": dot_border,
        }

    # ------------------------------------------------------------------
    def font_scale(self) -> float:
        try:
            user = float(self.settings.get("font_scale", 1.0))
        except (TypeError, ValueError):
            user = 1.0
        scale = self.mode.font_scale * user
        return max(0.6, min(4.0, scale))

    def bold(self) -> bool:
        return bool(self.mode.bold or self.settings.get("bold_text", False))

    def cell_scale(self) -> float:
        try:
            user = float(self.settings.get("braille_cell_scale", 1.0))
        except (TypeError, ValueError):
            user = 1.0
        return max(0.6, min(3.0, user))

    def line_spacing(self) -> float:
        """تباعد الأسطر داخل صناديق النصوص المتعدّدة الأسطر."""
        try:
            value = float(self.settings.get("line_spacing", 1.0))
        except (TypeError, ValueError):
            value = 1.0
        return max(1.0, min(2.5, value))

    def point_size(self, base: float = BASE_FONT_POINT_SIZE) -> float:
        return max(8.0, min(48.0, base * self.font_scale()))

    def make_font(self, base: float = BASE_FONT_POINT_SIZE) -> wx.Font:
        size = int(round(self.point_size(base)))
        font = wx.Font(
            size,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD if self.bold() else wx.FONTWEIGHT_NORMAL,
            faceName=FONT_CANDIDATES[0],
        )
        # استخدم خطًا عربيًا آخر إن لم يتوفّر الأول.
        if not font.IsOk() or not font.GetFaceName():
            for candidate in FONT_CANDIDATES[1:]:
                font = wx.Font(size, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                               wx.FONTWEIGHT_BOLD if self.bold() else wx.FONTWEIGHT_NORMAL,
                               faceName=candidate)
                if font.IsOk():
                    break
        return font

    def make_braille_font(self, point_size: float) -> wx.Font:
        size = int(max(8.0, round(point_size)))
        for candidate in BRAILLE_FONT_CANDIDATES:
            font = wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                           wx.FONTWEIGHT_NORMAL, faceName=candidate)
            if font.IsOk() and font.GetFaceName():
                return font
        return wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)


def apply_theme_to(window: wx.Window, theme: Theme) -> None:
    """طبّق الألوان والخط على نافذة وكل عناصرها الفرعية.

    لا يتغيّر أي شيء في إعدادات Windows أو قارئ الشاشة؛ التأثير محصور داخل
    التطبيق نفسه.
    """
    colours = theme.colors
    font = theme.make_font()
    bg = to_colour(colours["background"])
    surface = to_colour(colours["surface"])
    text = to_colour(colours["text"])

    def visit(win: wx.Window) -> None:
        try:
            keep_font = bool(getattr(win, "_keep_font", False))
            if isinstance(win, wx.StaticBox):
                # إطار البطاقة: نصّ بلون النص وخلفية بلون السطح.
                win.SetForegroundColour(text)
                win.SetBackgroundColour(surface)
            elif isinstance(win, wx.Panel):
                # البطاقات (التي تحمل السمة ``_surface``) تُلوَّن بلون السطح
                # لتبدو بارزة عن خلفية الشاشة، وبقية اللوحات بلون الخلفية.
                win.SetBackgroundColour(surface if getattr(win, "_surface", False) else bg)
            elif isinstance(win, wx.TextCtrl):
                win.SetBackgroundColour(surface)
                win.SetForegroundColour(text)
                try:
                    spacing = theme.line_spacing()
                    if spacing > 1.001 and (win.GetWindowStyleFlag() & wx.TE_MULTILINE):
                        last = win.GetLastPosition()
                        if last > 0:
                            attr = wx.TextAttr()
                            attr.SetLineSpacing(spacing)
                            win.SetStyle(0, last, attr)
                except Exception:
                    pass
            elif isinstance(win, wx.StaticText):
                win.SetForegroundColour(text)
            elif isinstance(win, (wx.Button, wx.CheckBox, wx.RadioButton,
                                 wx.Choice, wx.ListCtrl, wx.SpinCtrlDouble, wx.ColourPickerCtrl)):
                try:
                    win.SetForegroundColour(text)
                    win.SetBackgroundColour(surface)
                except Exception:
                    pass
            if not keep_font:
                try:
                    win.SetFont(font)
                except Exception:
                    pass
            for child in win.GetChildren():
                visit(child)
        except Exception:
            pass

    visit(window)
    try:
        window.Refresh()
    except Exception:
        pass
