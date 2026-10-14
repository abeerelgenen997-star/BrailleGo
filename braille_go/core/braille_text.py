"""تحويل النص إلى أنماط برايل والعكس، ومعالجة النصوص المختلطة.

This module is the bridge between printed text and braille patterns.  It
implements a *transcriber* for the two supported languages, Arabic and
English, in **uncontracted** form (one braille cell per printed letter), which
is exactly what the beginner curriculum needs.

Important conventions implemented here
-------------------------------------
* Arabic braille is read left-to-right and keeps the *logical* order of the
  letters: the first letter of the word is the leftmost cell.  For example
  "بريل عربية" is written ``⠃⠗⠊⠇ ⠷⠗⠃⠊⠡``.  The order of the cells therefore
  matches the order of the characters in the string; no visual reversal is
  applied.
* Digits are introduced by the number sign ``⠼`` (dots 3-4-5-6) and are read
  left-to-right.
* English capital letters are introduced by the capital sign ``⠠`` (dot 6).

Everything degrades gracefully: unknown characters are reported in the result
instead of raising, so the UI never crashes on odd user input.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .braille import BrailleCell, cells_to_unicode
from .braille_alphabet_ar import ARABIC_ALL_LETTERS
from .braille_alphabet_en import CAPITAL_SIGN_DOTS, ENGLISH_LETTERS
from .braille_diacritics import ARABIC_DIACRITICS
from .braille_digits import NUMBER_SIGN_DOTS
from .symbols import SymbolCategory, SymbolRepository, build_default_repository

#: Arabic-Indic digits and their western counterparts.
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_WESTERN_DIGITS = "0123456789"

#: Dot patterns of the digits, indexed by numeric value.
_DIGIT_CELLS = {
    "1": "1", "2": "12", "3": "14", "4": "145", "5": "15",
    "6": "124", "7": "1245", "8": "125", "9": "24", "0": "245",
}

#: Arabic characters that are ignorable for transcription.
_ARABIC_IGNORED = {
    "\u0640",  # tatweel
    "\u200c",  # ZWNJ
    "\u200d",  # ZWJ
    "\u200e",  # LRM
    "\u200f",  # RLM
    "\ufeff",  # BOM
}


@dataclass
class TranscriptionResult:
    """نتيجة تحويل نص إلى برايل."""

    source: str
    cells: tuple[BrailleCell, ...] = ()
    unknown: tuple[str, ...] = ()
    language: str = "ar"

    @property
    def unicode(self) -> str:
        return cells_to_unicode(self.cells)

    @property
    def dots(self) -> tuple[tuple[int, ...], ...]:
        return tuple(cell.dots for cell in self.cells)

    @property
    def is_complete(self) -> bool:
        return not self.unknown


def build_char_map(language: str, repository: SymbolRepository | None = None) -> dict[str, str]:
    """Return a ``{printed char: dot string}`` mapping for one language."""
    repo = repository or build_default_repository()
    mapping: dict[str, str] = {}
    if language == "ar":
        for entry in ARABIC_ALL_LETTERS:
            mapping.setdefault(entry.char, entry.dots)
        for entry in ARABIC_DIACRITICS:
            mapping.setdefault(entry.char, entry.dots)
    else:
        for entry in ENGLISH_LETTERS:
            mapping.setdefault(entry.char, entry.dots)
    return mapping


def _arabic_diacritics() -> dict[str, str]:
    return {entry.char: entry.dots for entry in ARABIC_DIACRITICS}


def transcribe(text: str, language: str = "ar") -> TranscriptionResult:
    """حوّل نصًا مطبوعًا إلى خلايا برايل.

    Parameters
    ----------
    text:
        النص المطبوع.
    language:
        ``"ar"`` أو ``"en"``.
    """
    result = TranscriptionResult(source=text, language=language)
    if text is None:
        return result

    cells: list[BrailleCell] = []
    unknown: list[str] = []

    if language == "ar":
        mapping = build_char_map("ar")
        diacritics = _arabic_diacritics()
        # Arabic braille keeps the logical order of the characters; the first
        # letter of the word becomes the leftmost cell.
        last_letter_index: int | None = None
        for char in text:
            if char in _ARABIC_IGNORED:
                continue
            if char in _WESTERN_DIGITS:
                cells.append(BrailleCell.from_dot_string(NUMBER_SIGN_DOTS))
                cells.append(BrailleCell.from_dot_string(_DIGIT_CELLS[char]))
                last_letter_index = None
                continue
            if char in _ARABIC_DIGITS:
                value = str(_ARABIC_DIGITS.index(char))
                cells.append(BrailleCell.from_dot_string(NUMBER_SIGN_DOTS))
                cells.append(BrailleCell.from_dot_string(_DIGIT_CELLS[value]))
                last_letter_index = None
                continue
            if char == " ":
                cells.append(BrailleCell.empty())
                last_letter_index = None
                continue
            if char == "\u0651":  # shadda is written *before* the consonant
                if last_letter_index is None:
                    cells.append(BrailleCell.from_dot_string(diacritics[char]))
                else:
                    cells.insert(last_letter_index, BrailleCell.from_dot_string(diacritics[char]))
                    last_letter_index += 1
                continue
            if char in diacritics:
                cells.append(BrailleCell.from_dot_string(diacritics[char]))
                continue
            dots = mapping.get(char)
            if dots is None:
                unknown.append(char)
                continue
            last_letter_index = len(cells)
            cells.append(BrailleCell.from_dot_string(dots))
    else:
        mapping = build_char_map("en")
        number_mode = False
        for char in text:
            if char.isdigit():
                if not number_mode:
                    cells.append(BrailleCell.from_dot_string(NUMBER_SIGN_DOTS))
                    number_mode = True
                cells.append(BrailleCell.from_dot_string(_DIGIT_CELLS[char]))
                continue
            number_mode = False
            if char == " ":
                cells.append(BrailleCell.empty())
                continue
            if char.isupper():
                lower = char.lower()
                dots = mapping.get(lower)
                if dots is None:
                    unknown.append(char)
                    continue
                cells.append(BrailleCell.from_dot_string(CAPITAL_SIGN_DOTS))
                cells.append(BrailleCell.from_dot_string(dots))
                continue
            dots = mapping.get(char)
            if dots is None:
                unknown.append(char)
                continue
            cells.append(BrailleCell.from_dot_string(dots))

    result.cells = tuple(cells)
    result.unknown = tuple(unknown)
    return result


def transcribe_word(word: str, language: str) -> str:
    """حوّل كلمة وأعد نمط برايل كسلسلة يونيكود (اختصار مريح)."""
    return transcribe(word, language).unicode


def reverse_lookup_dots(
    dots: tuple[int, ...],
    language: str,
    repository: SymbolRepository | None = None,
    categories: tuple[SymbolCategory, ...] | None = None,
) -> list[str]:
    """ابحث عن المحارف المطبوعة التي تطابق نمط نقاط معيّنًا."""
    repo = repository or build_default_repository()
    matches: list[str] = []
    for symbol in repo.all():
        if symbol.category == SymbolCategory.DIGIT:
            continue
        if categories is not None and symbol.category not in categories:
            continue
        if language == "ar" and symbol.language != "ar":
            continue
        if language == "en" and symbol.language != "en":
            continue
        if symbol.dots == tuple(sorted(dots)):
            if symbol.char not in matches:
                matches.append(symbol.char)
    return matches


def display_cells(text: str, language: str) -> str:
    """نمط برايل لعرض النص في الواجهة (نص فارغ عند التعذّر)."""
    try:
        return transcribe(text, language).unicode
    except Exception:  # pragma: no cover - defensive, must never crash the UI
        return ""
