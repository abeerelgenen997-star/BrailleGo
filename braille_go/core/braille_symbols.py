"""الرموز والعلامات الشائعة في برايل.

المصدر: جداول برايل الدولية (انظر BRAILLE_DATA_SOURCES.md).

تشمل هذه القائمة العلامات التي يحتاجها المتعلّم في القراءة اليومية:
علامة الرقم، علامة الحرف الكبير، علامة الحرف المميّز (التأكيد)، الفراغ،
وعلامات الاختصارات الشائعة في برايل العربي.
"""

from __future__ import annotations

from .braille_entries import MultiCellEntry

SYMBOLS: tuple[MultiCellEntry, ...] = (
    MultiCellEntry("sym_number_sign", "\u283c", ("3456",), "علامة الرقم", "number sign",
                   "تُكتب قبل الرقم أو مجموعة الأرقام. النقاط 3-4-5-6.",
                   language="ar", tags=("mark", "shared")),
    MultiCellEntry("sym_capital_sign", "\u2820", ("6",), "علامة الحرف الكبير",
                   "capital sign", "تُكتب قبل الحرف الإنجليزي الكبير. النقطة 6.",
                   language="en", tags=("mark", "shared")),
    MultiCellEntry("sym_emphasis", "\u2828", ("46",), "علامة التأكيد/التسطير",
                   "emphasis sign", "النقاط 4-6.", language="en", tags=("mark",)),
    MultiCellEntry("sym_decimal_point", "\u2828", ("46",), "الفاصلة العشرية",
                   "decimal point", "النقاط 4-6، وتختلف عن النقطة العادية.",
                   language="en", tags=("mark",)),
    MultiCellEntry("sym_space", " ", ("",), "فراغ", "space",
                   "الخلية الفارغة تفصل بين الكلمات.", language="ar", tags=("mark",)),
    MultiCellEntry("sym_abbreviation", "\u2808", ("4",), "علامة الاختصار", "abbreviation sign",
                   language="ar", tags=("mark",)),
    MultiCellEntry("sym_contraction_prefix", "\u2810", ("5",), "بادئة الاختصار",
                   "contraction prefix", language="en", tags=("mark",)),
    MultiCellEntry("sym_currency", "\u2809", ("14",), "علامة العملة", "currency sign",
                   language="en", tags=("mark",)),
)
