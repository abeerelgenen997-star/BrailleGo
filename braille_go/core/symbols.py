"""تمثيل الرموز وتجميعها في مستودع واحد.

This module defines the :class:`BrailleSymbol` value object and the
:class:`SymbolRepository` used by the rest of the application.  The raw data
lives in sibling modules (``braille_alphabet_ar``, ``braille_alphabet_en``,
``braille_digits``, ``braille_punctuation``, ``braille_diacritics``,
``braille_symbols``) and is assembled here so that nothing has to import the
GUI layer just to look up a braille pattern.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from .braille import BrailleCell, cells_to_unicode


class SymbolCategory(str, Enum):
    """التصنيفات التعليمية للرموز."""

    INTRODUCTION = "introduction"
    LETTER_AR = "letter_ar"
    LETTER_EN = "letter_en"
    DIGIT = "digit"
    PUNCTUATION = "punctuation"
    DIACRITIC = "diacritic"
    SYMBOL = "symbol"
    WORD = "word"
    SENTENCE = "sentence"
    CONTRACTION = "contraction"

    @property
    def label_ar(self) -> str:
        return _CATEGORY_LABELS_AR[self]


_CATEGORY_LABELS_AR: dict[SymbolCategory, str] = {
    SymbolCategory.INTRODUCTION: "مقدمة",
    SymbolCategory.LETTER_AR: "حرف عربي",
    SymbolCategory.LETTER_EN: "حرف إنجليزي",
    SymbolCategory.DIGIT: "رقم",
    SymbolCategory.PUNCTUATION: "علامة ترقيم",
    SymbolCategory.DIACRITIC: "تشكيل",
    SymbolCategory.SYMBOL: "رمز",
    SymbolCategory.WORD: "كلمة",
    SymbolCategory.SENTENCE: "جملة",
    SymbolCategory.CONTRACTION: "اختصار",
}


@dataclass(frozen=True)
class BrailleSymbol:
    """رمز برايل واحد مع بياناته الوصفية.

    Attributes
    ----------
    key:
        معرّف ثابت وفريد، مثل ``ar_alif`` أو ``en_a`` أو ``digit_1``.
    char:
        النص المطبوع المقابل (حرف/رقم/علامة). قد يكون أكثر من محرف للرموز المركبة.
    cells:
        خلايا برايل المكوّنة للرمز (عادة خلية واحدة).
    category:
        التصنيف التعليمي.
    name_ar / name_en:
        اسم الرمز بالعربية والإنجليزية.
    notes_ar:
        ملاحظة تعليمية تظهر في التغذية الراجعة.
    prefix_cells:
        خلايا بادئة تُكتب قبل الرمز (مثل علامة الرقم ⠼ أو علامة الحرف الكبير ⠠).
    """

    key: str
    char: str
    cells: tuple[BrailleCell, ...]
    category: SymbolCategory
    name_ar: str
    name_en: str = ""
    notes_ar: str = ""
    prefix_cells: tuple[BrailleCell, ...] = field(default_factory=tuple)
    language: str = "ar"

    # ------------------------------------------------------------------
    @property
    def cell(self) -> BrailleCell:
        """الخلية الأولى (الأكثر شيوعًا: رمز من خلية واحدة)."""
        return self.cells[0] if self.cells else BrailleCell.empty()

    @property
    def dots(self) -> tuple[int, ...]:
        return self.cell.dots

    @property
    def is_multicell(self) -> bool:
        return len(self.cells) > 1

    def pattern_unicode(self) -> str:
        """نمط برايل بدون علامات البادئة."""
        return cells_to_unicode(self.cells)

    def full_unicode(self) -> str:
        """نمط برايل كامل مع علامات البادئة (علامة الرقم/الحرف الكبير)."""
        return cells_to_unicode((*self.prefix_cells, *self.cells))

    def full_unicode_with_space(self) -> str:
        """النمط الكامل مع فراغ في نهاية كل خلية لسهولة القراءة."""
        text = self.full_unicode()
        return "\u200b".join(text)

    def dots_text(self) -> str:
        """تمثيل نصي للنقاط لكل الخلايا، مثل ``"145"`` أو ``"5|2"``."""
        return " | ".join(c.to_dot_string("") or "-" for c in self.cells)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.key}({self.dots_text()})"


class SymbolRepository:
    """مستودع للبحث عن الرموز بمفاتيحها أو محارفها."""

    def __init__(self, symbols: Iterable[BrailleSymbol]) -> None:
        self._by_key: dict[str, BrailleSymbol] = {}
        for symbol in symbols:
            if symbol.key in self._by_key:
                raise ValueError(f"مفتاح مكرر في بيانات برايل: {symbol.key}")
            self._by_key[symbol.key] = symbol
        self._by_char_ar: dict[str, list[BrailleSymbol]] = {}
        self._by_char_en: dict[str, list[BrailleSymbol]] = {}
        for symbol in self._by_key.values():
            target = self._by_char_ar if symbol.language == "ar" else self._by_char_en
            target.setdefault(symbol.char, []).append(symbol)

    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._by_key)

    def __contains__(self, key: object) -> bool:
        return key in self._by_key

    def get(self, key: str) -> BrailleSymbol | None:
        return self._by_key.get(key)

    def require(self, key: str) -> BrailleSymbol:
        symbol = self._by_key.get(key)
        if symbol is None:
            raise KeyError(f"رمز برايل غير معروف: {key}")
        return symbol

    def all(self) -> tuple[BrailleSymbol, ...]:
        return tuple(self._by_key.values())

    def by_category(self, *categories: SymbolCategory) -> list[BrailleSymbol]:
        wanted = set(categories)
        return [s for s in self._by_key.values() if s.category in wanted]

    def find_by_char(self, char: str, language: str | None = None) -> list[BrailleSymbol]:
        """ابحث عن رمز حسب النص المطبوع."""
        if language == "ar":
            return list(self._by_char_ar.get(char, ()))
        if language == "en":
            return list(self._by_char_en.get(char, ()))
        return list(self._by_char_ar.get(char, ())) + list(self._by_char_en.get(char, ()))

    def find_by_dots(self, dots: tuple[int, ...]) -> list[BrailleSymbol]:
        """كل الرموز التي تطابق نمط النقاط المعطى (قد تكون أكثر من واحد)."""
        wanted = tuple(sorted(dots))
        return [s for s in self._by_key.values() if s.dots == wanted]

    def many(self, keys: Iterable[str]) -> list[BrailleSymbol]:
        result: list[BrailleSymbol] = []
        for key in keys:
            symbol = self._by_key.get(key)
            if symbol is not None:
                result.append(symbol)
        return result


# ----------------------------------------------------------------------
# بيانات المصادر (تُجمَّع من الوحدات المتخصصة)
# ----------------------------------------------------------------------
def _cell(*dot_specs: str) -> tuple[BrailleCell, ...]:
    return tuple(BrailleCell.from_dot_string(spec) for spec in dot_specs)


def build_default_repository() -> SymbolRepository:
    """ابنِ المستودع الافتراضي من كل بيانات برايل المعرّفة في التطبيق."""
    from . import braille_alphabet_ar as ar
    from . import braille_alphabet_en as en
    from . import braille_diacritics as dia
    from . import braille_digits as dig
    from . import braille_punctuation as punc
    from . import braille_symbols as sym

    symbols: list[BrailleSymbol] = []

    for entry in ar.ARABIC_ALL_LETTERS:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(entry.dots),
                category=SymbolCategory.LETTER_AR,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                language="ar",
            )
        )

    for entry in en.ENGLISH_LETTERS:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(entry.dots),
                category=SymbolCategory.LETTER_EN,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                language="en",
            )
        )

    for entry in dig.DIGITS:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(entry.dots),
                category=SymbolCategory.DIGIT,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                prefix_cells=_cell(dig.NUMBER_SIGN_DOTS),
                language="ar",
            )
        )

    for entry in dia.ARABIC_DIACRITICS:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(entry.dots),
                category=SymbolCategory.DIACRITIC,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                language="ar",
            )
        )

    for entry in punc.PUNCTUATION:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(*entry.dots),
                category=SymbolCategory.PUNCTUATION,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                language=entry.language,
            )
        )

    for entry in sym.SYMBOLS:
        symbols.append(
            BrailleSymbol(
                key=entry.key,
                char=entry.char,
                cells=_cell(*entry.dots),
                category=SymbolCategory.SYMBOL,
                name_ar=entry.name_ar,
                name_en=entry.name_en,
                notes_ar=entry.notes_ar,
                language=entry.language,
            )
        )

    return SymbolRepository(symbols)
