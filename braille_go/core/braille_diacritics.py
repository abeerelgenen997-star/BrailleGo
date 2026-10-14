"""التشكيل العربي بطريقة برايل.

المصدر: جدول برايل العربي الموحّد (انظر BRAILLE_DATA_SOURCES.md).

ملاحظتان مهمّتان:
1. الحركات في برايل العربي ليست حروفًا قصيرة، بل علامات تُكتب بعد الحرف،
   وهي اختيارية وتُحذف عادةً كما في الطباعة العربية.
2. الشدّة ⠠ تُكتب *قبل* الحرف المشدّد، أما السكون والحركات فتُكتب *بعد* الحرف.
"""

from __future__ import annotations

from .braille_entries import SymbolEntry

ARABIC_DIACRITICS: tuple[SymbolEntry, ...] = (
    SymbolEntry("dia_fatha", "\u064e", "2", "فتحة", "fatha", "تُكتب بعد الحرف، وهي النقطة 2."),
    SymbolEntry("dia_damma", "\u064f", "136", "ضمة", "damma", "تُكتب بعد الحرف."),
    SymbolEntry("dia_kasra", "\u0650", "15", "كسرة", "kasra", "تُكتب بعد الحرف."),
    SymbolEntry("dia_fathatan", "\u064b", "23", "فتحتان", "fathatan"),
    SymbolEntry("dia_dammatan", "\u064c", "26", "ضمتان", "dammatan"),
    SymbolEntry("dia_kasratan", "\u064d", "35", "كسرتان", "kasratan"),
    SymbolEntry("dia_sukun", "\u0652", "25", "سكون", "sukun", "تُكتب بعد الحرف."),
    SymbolEntry("dia_shadda", "\u0651", "6", "شدّة", "shadda", "تُكتب قبل الحرف المشدّد."),
)

#: مفاتيح التشكيل مرتّبة تربويًا.
DIACRITIC_ORDER: tuple[str, ...] = tuple(entry.key for entry in ARABIC_DIACRITICS)
