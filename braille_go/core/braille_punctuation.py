"""علامات الترقيم في برايل العربي والإنجليزي.

المصدر: جدول برايل العربي الموحّد وجدول برايل الإنجليزي (انظر
BRAILLE_DATA_SOURCES.md).

⚠ تنبيه مهم: تختلف علامات الترقيم بين الأنظمة اختلافًا كبيرًا. في هذا الملف
نفصل بوضوح بين *الترقيم العربي المشترك* (المستخدم في المشرق العربي) و
*الترقيم العربي الموحّد* (توصيات مؤتمر 2002) و*الترقيم الإنجليزي*، حتى لا
يختلط على المتعلّم نظامان مختلفان.
"""

from __future__ import annotations

from .braille_entries import MultiCellEntry

#: علامة الرقم وعلامة الحرف الكبير تُستخدمان كبادئات.
NUMBER_SIGN = "3456"
CAPITAL_SIGN = "6"

PUNCTUATION: tuple[MultiCellEntry, ...] = (
    # ------------------------------------------------------------------
    # الترقيم العربي المشترك
    # ------------------------------------------------------------------
    MultiCellEntry("punct_ar_comma", "،", ("5",), "فاصلة عربية (،)", "Arabic comma",
                   "في الترقيم العربي المشترك هي النقطة 5.", language="ar",
                   tags=("ar_common",)),
    MultiCellEntry("punct_ar_semicolon", "؛", ("56",), "فاصلة منقوطة (؛)", "Arabic semicolon",
                   language="ar", tags=("ar_common",)),
    MultiCellEntry("punct_ar_colon", ":", ("5", "2"), "نقطتان (:)", "colon",
                   "تُكتب بخلية الفاصلة العربية ثم خلية الفاصلة الإنجليزية.", language="ar",
                   tags=("ar_common",)),
    MultiCellEntry("punct_ar_period", ".", ("256",), "نقطة (.)", "period",
                   "النقاط 2-5-6، وهي نفس العلامة في النظام الإنجليزي.", language="ar",
                   tags=("ar_common", "shared")),
    MultiCellEntry("punct_ar_exclamation", "!", ("235",), "علامة تعجّب (!)", "exclamation mark",
                   "النقاط 2-3-5.", language="ar", tags=("ar_common", "shared")),
    MultiCellEntry("punct_ar_question", "؟", ("236",), "علامة استفهام عربية (؟)", "question mark",
                   "النقاط 2-3-6.", language="ar", tags=("ar_common", "shared")),
    MultiCellEntry("punct_ar_hyphen", "-", ("36",), "شرطة (-)", "hyphen",
                   "النقاط 3-6.", language="ar", tags=("ar_common", "shared")),

    # ------------------------------------------------------------------
    # الترقيم العربي الموحّد (توصيات 2002)
    # ------------------------------------------------------------------
    MultiCellEntry("punct_ar_u_quote", "\u201c\u2026\u201d", ("2356", "2356"),
                   "علامتا تنصيص “…” (الموحّد)", "quotation marks (unified)",
                   "في الترقيم العربي الموحّد: خليتان 2-3-5-6 تحيطان بالنص.",
                   language="ar", tags=("ar_unified",)),
    MultiCellEntry("punct_ar_u_paren", "(\u2026)", ("236", "356"),
                   "قوسان (…) (الموحّد)", "parentheses (unified)",
                   "في الترقيم العربي الموحّد: 2-3-6 قبل، و3-5-6 بعد.", language="ar",
                   tags=("ar_unified",)),
    MultiCellEntry("punct_ar_u_bracket", "[\u2026]", ("6", "236", "356", "3"),
                   "قوسان معقوفان […] (الموحّد)", "brackets (unified)",
                   language="ar", tags=("ar_unified",)),
    MultiCellEntry("punct_ar_u_brace", "{\u2026}", ("5", "236", "356", "2"),
                   "قوسان معقوفان {} (الموحّد)", "braces (unified)",
                   language="ar", tags=("ar_unified",)),
    MultiCellEntry("punct_ar_u_underline", "_\u2026_", ("6", "36"),
                   "تسطير (الموحّد)", "underlining (unified)",
                   language="ar", tags=("ar_unified",)),

    # ------------------------------------------------------------------
    # الترقيم الإنجليزي (UEB / الدرجة الأولى)
    # ------------------------------------------------------------------
    MultiCellEntry("punct_en_comma", ",", ("2",), "comma (,)", "comma",
                   "English punctuation, dots 2.", language="en", tags=("en",)),
    MultiCellEntry("punct_en_semicolon", ";", ("23",), "semicolon (;)", "semicolon",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_colon", ":", ("25",), "colon (:)", "colon",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_period", ".", ("256",), "period (.)", "period",
                   language="en", tags=("en", "shared")),
    MultiCellEntry("punct_en_exclamation", "!", ("235",), "exclamation mark (!)",
                   "exclamation mark", language="en", tags=("en", "shared")),
    MultiCellEntry("punct_en_question", "?", ("236",), "question mark (?)", "question mark",
                   language="en", tags=("en", "shared")),
    MultiCellEntry("punct_en_apostrophe", "'", ("3",), "apostrophe (')", "apostrophe",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_quote_open", "\u201c", ("236",), "opening quotation (\u201c)",
                   "opening quotation mark", language="en", tags=("en",)),
    MultiCellEntry("punct_en_quote_close", "\u201d", ("356",), "closing quotation (\u201d)",
                   "closing quotation mark", language="en", tags=("en",)),
    MultiCellEntry("punct_en_hyphen", "-", ("36",), "hyphen (-)", "hyphen",
                   language="en", tags=("en", "shared")),
    MultiCellEntry("punct_en_paren_open", "(", ("2356",), "opening parenthesis ((",
                   "opening parenthesis", language="en", tags=("en",)),
    MultiCellEntry("punct_en_paren_close", ")", ("2356",), "closing parenthesis ())",
                   "closing parenthesis", language="en", tags=("en",)),
    MultiCellEntry("punct_en_slash", "/", ("34",), "slash (/)", "slash",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_asterisk", "*", ("35",), "asterisk (*)", "asterisk",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_ampersand", "&", ("12346",), "ampersand (&)", "ampersand",
                   language="en", tags=("en",)),
    MultiCellEntry("punct_en_at", "@", ("4",), "at sign (@)", "at sign",
                   language="en", tags=("en",)),
)
