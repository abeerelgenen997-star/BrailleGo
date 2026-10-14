"""الحروف العربية بطريقة برايل.

المصدر: جدول برايل العربي الموحّد (انظر BRAILLE_DATA_SOURCES.md).
يرمز كل حرف بخلية واحدة، وتُقرأ برايل العربية من اليسار إلى اليمين.
"""

from __future__ import annotations

from .braille_entries import SymbolEntry

#: الحروف العربية الأساسية مرتبة تربويًا (من الأسهل إلى الأكثر تعقيدًا).
ARABIC_LETTERS: tuple[SymbolEntry, ...] = (
    SymbolEntry("ar_alif", "ا", "1", "ألف", "alif", "أبسط الحروف: النقطة 1 فقط."),
    SymbolEntry("ar_ba", "ب", "12", "باء", "ba", "النقطة 1 مع النقطة 2."),
    SymbolEntry("ar_ta", "ت", "2345", "تاء", "ta", "تشبه حرف الجيم مع اختلاف النقاط."),
    SymbolEntry("ar_tha", "ث", "1456", "ثاء", "tha"),
    SymbolEntry("ar_jeem", "ج", "245", "جيم", "jeem"),
    SymbolEntry("ar_hha", "ح", "156", "حاء", "hha"),
    SymbolEntry("ar_kha", "خ", "1346", "خاء", "kha"),
    SymbolEntry("ar_dal", "د", "145", "دال", "dal"),
    SymbolEntry("ar_thal", "ذ", "2346", "ذال", "dhal"),
    SymbolEntry("ar_ra", "ر", "1235", "راء", "ra"),
    SymbolEntry("ar_zay", "ز", "1356", "زاي", "zay"),
    SymbolEntry("ar_seen", "س", "234", "سين", "seen"),
    SymbolEntry("ar_sheen", "ش", "146", "شين", "sheen"),
    SymbolEntry("ar_sad", "ص", "12346", "صاد", "sad"),
    SymbolEntry("ar_dad", "ض", "1246", "ضاد", "dad"),
    SymbolEntry("ar_taa", "ط", "23456", "طاء", "taa"),
    SymbolEntry("ar_zha", "ظ", "123456", "ظاء", "zha", "يحتل جميع النقاط الست."),
    SymbolEntry("ar_ain", "ع", "12356", "عين", "ain"),
    SymbolEntry("ar_ghain", "غ", "126", "غين", "ghain"),
    SymbolEntry("ar_fa", "ف", "124", "فاء", "fa"),
    SymbolEntry("ar_qaf", "ق", "12345", "قاف", "qaf"),
    SymbolEntry("ar_kaf", "ك", "13", "كاف", "kaf"),
    SymbolEntry("ar_lam", "ل", "123", "لام", "lam"),
    SymbolEntry("ar_meem", "م", "134", "ميم", "meem"),
    SymbolEntry("ar_noon", "ن", "1345", "نون", "noon"),
    SymbolEntry("ar_ha", "ه", "125", "هاء", "ha"),
    SymbolEntry("ar_waw", "و", "2456", "واو", "waw"),
    SymbolEntry("ar_ya", "ي", "24", "ياء", "ya"),
)

#: ألف مقصورة وحروف الهمزة والتاء المربوطة — مجموعة متقدمة.
ARABIC_LETTERS_EXTENDED: tuple[SymbolEntry, ...] = (
    SymbolEntry("ar_alef_maksura", "ى", "135", "ألف مقصورة", "alef maksura"),
    SymbolEntry("ar_ta_marbuta", "ة", "16", "تاء مربوطة", "ta marbuta"),
    SymbolEntry("ar_hamza", "ء", "3", "همزة مفردة", "hamza"),
    SymbolEntry("ar_alef_hamza_above", "أ", "34", "ألف بهمزة فوقها", "alef with hamza above"),
    SymbolEntry("ar_alef_hamza_below", "إ", "46", "ألف بهمزة تحتها", "alef with hamza below"),
    SymbolEntry("ar_alef_madda", "آ", "345", "ألف ممدودة", "alef with madda"),
    SymbolEntry("ar_waw_hamza", "ؤ", "1256", "واو بهمزة", "waw with hamza"),
    SymbolEntry("ar_ya_hamza", "ئ", "13456", "ياء بهمزة", "ya with hamza"),
)

#: تراكيب شائعة تُكتب بخلية واحدة في برايل العربي.
ARABIC_LIGATURES: tuple[SymbolEntry, ...] = (
    SymbolEntry("ar_lig_al_lam", "ال", "14", "لام ألف معكوسة (ال)", "al-lam ligature"),
    SymbolEntry("ar_lig_lam_alef", "لا", "1236", "لام ألف (لا)", "lam-alef ligature"),
    SymbolEntry("ar_lig_aw", "أو", "246", "واو مع ألف (أو)", "aw ligature"),
)

#: كل الحروف والتراكيب.
ARABIC_ALL_LETTERS: tuple[SymbolEntry, ...] = (
    ARABIC_LETTERS + ARABIC_LETTERS_EXTENDED + ARABIC_LIGATURES
)
