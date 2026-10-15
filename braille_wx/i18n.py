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
        "mode_low_vision": "خلفية كريمية مريحة للعين",
        "mode_deuteranopia": "مناسب لعمى الألوان (أزرق/برتقالي)",
        "mode_grayscale": "رمادي بلا ألوان",
        "mode_dyslexia": "عسر القراءة (تباعد وخط أوضح)",
        "mode_protanopia": "عمى الألوان الأحمر/الأخضر",
        "mode_tritanopia": "عمى الألوان الأزرق/الأصفر",
        "mode_sepia": "سيبيا (قراءة طويلة مريحة)",
        "mode_oled": "أسود نقي (شاشات OLED وحساسية الضوء)",
        "mode_soft_pastel": "ألوان هادئة (حساسية حسّية)",
        "mode_senior": "كبار السن (كبير وتباين عالٍ)",
        "user_profile": "فئة المستخدم",
        "user_profile_desc": "اختر فئتك ليضبط التطبيق الإعدادات المناسبة تلقائيًا، ويمكنك تعديلها بعد ذلك.",
        "profile_instructor": "مدرب / مدربة",
        "profile_instructor_desc": "يفعّل أدوات المدرب: إدارة المتدربين والتقارير وتصدير CSV.",
        "profile_sighted": "متدرب مبصر",
        "profile_sighted_desc": "مبتدئ مبصر يتعلّم أساسيات برايل بالقراءة والنظر.",
        "profile_blind": "متعلّم كفيف",
        "profile_blind_desc": "يعتمد على قارئ الشاشة والنطق؛ يفعّل النطق والإرشادات والتباين العالي.",
        "profile_low_vision": "متعلّم ضعيف بصر",
        "profile_low_vision_desc": "يحتاج تكبيرًا وتباينًا عاليًا وألوانًا واضحة.",
        "profile_applied": "تم تطبيق إعدادات فئة المستخدم: {name}",
        "instructor_mode": "وضع المدرب (أدوات إدارة المتدربين والتقارير)",
        "encouragement_enabled": "أصوات وعبارات التشجيع",
        "welcome_tune_enabled": "موسيقى الترحيب عند أول تشغيل",
        "welcome_speech_enabled": "نطق كلمة الترحيب عند أول تشغيل",
        "announce_symbols": "نطق الحرف/الرقم تلقائيًا عند عرضه",
        "audio_section": "الصوت والنطق والتشجيع",
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
        "answer_wrong_or_empty": "أدخل إجابة في الحقل ثم اضغط مفتاح الإدخال (Enter) للتأكيد.",
        "goto_question": "مربع السؤال",
        "scroll_up": "تحريك لأعلى",
        "scroll_down": "تحريك لأسفل",
        "alphabet_guide": "دليل الحروف والأرقام",
        "alphabet_desc": "استعرض كل حرف ورقم واسمع نطقه من داخل التطبيق مع ظهور نمط برايل ونقاطه.",
        "letters_ar": "الحروف العربية",
        "letters_en": "الحروف الإنجليزية",
        "digits_section": "الأرقام",
        "speak_symbol": "اضغط لسماع النطق",
        "symbol_played": "تم نطق: {name}",
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
        "mode_low_vision": "Warm cream background (easy on the eyes)",
        "mode_deuteranopia": "Colour-blind friendly (blue/orange)",
        "mode_grayscale": "Grayscale",
        "mode_dyslexia": "Dyslexia friendly (clearer spacing)",
        "mode_protanopia": "Red/green colour blindness",
        "mode_tritanopia": "Blue/yellow colour blindness",
        "mode_sepia": "Sepia (comfortable long reading)",
        "mode_oled": "True black (OLED & light sensitivity)",
        "mode_soft_pastel": "Soft pastel (sensory friendly)",
        "mode_senior": "Senior (large & high contrast)",
        "user_profile": "User type",
        "user_profile_desc": "Pick your user type and the app applies suitable settings automatically; you can still adjust them.",
        "profile_instructor": "Instructor",
        "profile_instructor_desc": "Enables instructor tools: manage learners, reports and CSV export.",
        "profile_sighted": "Sighted learner",
        "profile_sighted_desc": "A sighted beginner learning the basics of braille visually.",
        "profile_blind": "Blind learner",
        "profile_blind_desc": "Relies on screen reader and speech; enables speech, guidance and high contrast.",
        "profile_low_vision": "Low-vision learner",
        "profile_low_vision_desc": "Needs enlargement, high contrast and clear colours.",
        "profile_applied": "Applied user type settings: {name}",
        "instructor_mode": "Instructor mode (learner management and reports)",
        "encouragement_enabled": "Encouragement sounds and phrases",
        "welcome_tune_enabled": "Welcome music on first run",
        "welcome_speech_enabled": "Spoken welcome on first run",
        "announce_symbols": "Speak the letter/number automatically",
        "audio_section": "Sound, speech and encouragement",
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
        "answer_wrong_or_empty": "Type an answer, then press Enter to confirm.",
        "goto_question": "Question box",
        "scroll_up": "Scroll up",
        "scroll_down": "Scroll down",
        "alphabet_guide": "Letters and numbers guide",
        "alphabet_desc": "Browse every letter and number and hear it spoken by the app, with its braille pattern and dots.",
        "letters_ar": "Arabic letters",
        "letters_en": "English letters",
        "digits_section": "Numbers",
        "speak_symbol": "Press to hear",
        "symbol_played": "Played: {name}",
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
