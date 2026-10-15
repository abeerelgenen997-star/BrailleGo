"""طبقة ترجمة للواجهة الجديدة تبني فوق ``braille_go.core.i18n``.

المفاتيح القديمة موجودة في الوحدة الأساسية، وهنا نضيف المفاتيح الجديدة
الخاصة بواجهة wx (أنماط العرض، الاختصارات، المثبّت، ...).
"""

from __future__ import annotations

from braille_go.core import i18n as _base

#: مفاتيح إضافية خاصة بواجهة wx.
EXTRA: dict[str, dict[str, str]] = {
    "ar": {
        "app_title": "Braille Go — تعلّم برايل",
        "question_box": "نص السؤال (صندوق كتابة قابل للقراءة)",
        "question_box_hint": "يمكنك التركيز على هذا الحقل في أي وقت بالاختصار Ctrl+E.",
        "answer_box": "حقل إدخال الإجابة",
        "feedback_box": "نتيجة الإجابة",
        "stimulus_box": "المطلوب قراءته",
        "shortcuts": "اختصارات لوحة المفاتيح",
        "shortcuts_hint": "كل وظائف التطبيق لها اختصار لوحة مفاتيح.",
        "display_mode": "نمط العرض",
        "display_mode_desc": "أنماط جاهزة تناسب مختلف أنواع الإعاقة البصرية.",
        "mode_normal_light": "عادي (فاتح)",
        "mode_normal_dark": "عادي (داكن)",
        "mode_hc_light": "تباين عالٍ (أبيض/أسود)",
        "mode_hc_dark": "تباين عالٍ (أسود/أصفر)",
        "mode_yellow_black": "أصفر على أسود (ضعف بصر شديد)",
        "mode_large_print": "طباعة كبيرة",
        "mode_low_vision": "عسر القراءة (خلفية كريمية وتباعد واسع)",
        "mode_deuteranopia": "مناسب لعمى الألوان (أزرق/برتقالي)",
        "mode_grayscale": "رمادي بلا ألوان",
        "font_scale": "حجم الخط",
        "line_spacing": "تباعد الأسطر",
        "bold_text": "نص عريض",
        "clear_question": "مسح الإجابة",
        "show_answer_box": "إظهار حقل إدخال الإجابة",
        "menu_file": "ملف",
        "menu_go": "الانتقال",
        "menu_learn": "التعلّم",
        "menu_view": "العرض",
        "menu_help": "مساعدة",
        "quit": "خروج",
        "save_settings_ok": "تم حفظ الإعدادات وتطبيقها.",
        "reset_settings_ok": "تمت إعادة الإعدادات إلى الافتراضي.",
        "installer_hint": "يمكن تثبيت البرنامج على الجهاز عبر ملف التثبيت (Installer).",
        "speech_status": "حالة النطق",
        "sounds_status": "حالة الأصوات",
        "answer_wrong_or_empty": "أدخل إجابة في الحقل ثم اضغط تأكيد (Ctrl+Enter).",
        "goto_question": "مربع السؤال",
        "scroll_up": "تحريك لأعلى",
        "scroll_down": "تحريك لأسفل",
    },
    "en": {
        "app_title": "Braille Go — Learn Braille",
        "question_box": "Question text (accessible edit box)",
        "question_box_hint": "Focus this box any time with Ctrl+E.",
        "answer_box": "Answer input box",
        "feedback_box": "Answer result",
        "stimulus_box": "What to read",
        "shortcuts": "Keyboard shortcuts",
        "shortcuts_hint": "Every action in the app has a keyboard shortcut.",
        "display_mode": "Display mode",
        "display_mode_desc": "Presets that suit different kinds of visual impairment.",
        "mode_normal_light": "Normal (light)",
        "mode_normal_dark": "Normal (dark)",
        "mode_hc_light": "High contrast (white/black)",
        "mode_hc_dark": "High contrast (black/yellow)",
        "mode_yellow_black": "Yellow on black (severe low vision)",
        "mode_large_print": "Large print",
        "mode_low_vision": "Dyslexia friendly (cream, wide spacing)",
        "mode_deuteranopia": "Colour-blind friendly (blue/orange)",
        "mode_grayscale": "Grayscale",
        "font_scale": "Font size",
        "line_spacing": "Line spacing",
        "bold_text": "Bold text",
        "clear_question": "Clear answer",
        "show_answer_box": "Show answer input box",
        "menu_file": "File",
        "menu_go": "Go",
        "menu_learn": "Learn",
        "menu_view": "View",
        "menu_help": "Help",
        "quit": "Quit",
        "save_settings_ok": "Settings saved and applied.",
        "reset_settings_ok": "Settings reset to defaults.",
        "installer_hint": "The program can be installed with the provided installer.",
        "speech_status": "Speech status",
        "sounds_status": "Sound status",
        "answer_wrong_or_empty": "Type an answer, then press Confirm (Ctrl+Enter).",
        "goto_question": "Question box",
        "scroll_up": "Scroll up",
        "scroll_down": "Scroll down",
    },
}


def set_lang(lang: str) -> None:
    _base.set_lang(lang)


def get_lang() -> str:
    return _base.get_lang()


def t(key: str, **kwargs) -> str:
    """أعد النص المترجم للمفتاح، مع الرجوع للعربية عند غياب الترجمة."""
    lang = _base.get_lang()
    text = None
    for table in (EXTRA.get(lang, {}), _base.STRINGS.get(lang, {}), EXTRA["ar"], _base.STRINGS["ar"]):
        if key in table:
            text = table[key]
            break
    if text is None:
        text = key
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text


def is_rtl() -> bool:
    return get_lang() == "ar"
