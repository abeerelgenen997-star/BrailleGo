"""نموذج خلية برايل والأدوات المساعدة للتحويل.

Braille cell model
==================

A braille cell consists of six dots arranged in two columns::

    النقطة 1    النقطة 4
    النقطة 2    النقطة 5
    النقطة 3    النقطة 6

The model in this module supports the 8-dot Unicode braille range (U+2800 to
U+28FF) so that future extensions do not require a redesign, but the
application only ever renders the standard six dots.

Dot numbering follows the international convention:

======  ======  ==============
Dot     Column  Row
======  ======  ==============
1       left    top
2       left    middle
3       left    bottom
4       right   top
5       right   middle
6       right   bottom
7       left    (8-dot extension)
8       right   (8-dot extension)
======  ======  ==============

All conversions are pure functions; nothing in this module touches the GUI or
the database, which makes the logic trivially unit-testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

#: Number of dots used by the standard braille cell.
STANDARD_DOT_COUNT = 6

#: Number of dots in the extended (computer) braille cell.
EXTENDED_DOT_COUNT = 8

#: First code point of the Unicode "Braille Patterns" block.
BRAILLE_UNICODE_BASE = 0x2800

#: Highest code point of the Unicode "Braille Patterns" block.
BRAILLE_UNICODE_MAX = 0x28FF

#: Blank braille cell (space for braille).
BLANK_CELL_CHAR = "\u2800"

#: Human readable names for every dot, in reading order.
DOT_NAMES_AR: dict[int, str] = {
    1: "النقطة 1",
    2: "النقطة 2",
    3: "النقطة 3",
    4: "النقطة 4",
    5: "النقطة 5",
    6: "النقطة 6",
    7: "النقطة 7",
    8: "النقطة 8",
}

#: Short labels used inside the interactive cell widget.
DOT_SHORT_AR: dict[int, str] = {n: str(n) for n in range(1, 9)}

#: Position of each dot on a 3-row x 2-column grid: (row, column).
DOT_GRID_POSITION: dict[int, tuple[int, int]] = {
    1: (0, 0),
    2: (1, 0),
    3: (2, 0),
    4: (0, 1),
    5: (1, 1),
    6: (2, 1),
    7: (3, 0),
    8: (3, 1),
}

#: Grid position (row, column) -> dot number.
GRID_DOT_LOOKUP: dict[tuple[int, int], int] = {
    pos: dot for dot, pos in DOT_GRID_POSITION.items()
}


class BrailleError(ValueError):
    """Raised when braille data is malformed."""


def _validate_dot(dot: int) -> int:
    if not isinstance(dot, int) or isinstance(dot, bool):
        raise BrailleError(f"رقم النقطة يجب أن يكون عددًا صحيحًا، وليس {dot!r}")
    if not 1 <= dot <= EXTENDED_DOT_COUNT:
        raise BrailleError(f"رقم النقطة خارج المدى المسموح (1-8): {dot}")
    return dot


@dataclass(frozen=True, order=True)
class BrailleCell:
    """خلية برايل غير قابلة للتعديل تمثل مجموعة من النقاط.

    >>> BrailleCell.from_dots("145")
    BrailleCell(dots=(1, 4, 5))
    >>> str(BrailleCell.from_dots("145"))
    '⠙'
    """

    dots: tuple[int, ...] = ()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    def __post_init__(self) -> None:
        normalised = tuple(sorted({_validate_dot(d) for d in self.dots}))
        object.__setattr__(self, "dots", normalised)

    @classmethod
    def empty(cls) -> "BrailleCell":
        """Return an empty cell."""
        return cls(())

    @classmethod
    def from_dots(cls, dots: Iterable[int | str]) -> "BrailleCell":
        """Build a cell from an iterable of dot numbers."""
        values = []
        for d in dots:
            if isinstance(d, str) and d.isdigit():
                values.append(int(d))
            elif isinstance(d, int) and not isinstance(d, bool):
                values.append(d)
            else:
                raise BrailleError(f"رقم النقطة يجب أن يكون عددًا صحيحًا، وليس {d!r}")
        return cls(tuple(values))

    @classmethod
    def from_dot_string(cls, spec: str) -> "BrailleCell":
        """Build a cell from a compact string such as ``"145"`` or ``"1-4-5"``.

        Empty input (or ``"-"``) produces an empty cell.
        """
        if spec is None:
            raise BrailleError("لا يمكن إنشاء خلية من قيمة فارغة")
        text = str(spec).strip().replace("-", "").replace(",", "").replace(" ", "")
        if not text:
            return cls.empty()
        if not text.isdigit():
            raise BrailleError(f"صيغة نقاط غير صحيحة: {spec!r}")
        return cls(tuple(int(ch) for ch in text))

    @classmethod
    def from_bitmask(cls, mask: int) -> "BrailleCell":
        """Build a cell from a bit mask where bit 0 is dot 1, bit 1 is dot 2..."""
        if mask is None:
            raise BrailleError("قناع البتات لا يمكن أن يكون فارغًا")
        if mask < 0:
            raise BrailleError("قناع البتات لا يمكن أن يكون سالبًا")
        dots = [n + 1 for n in range(EXTENDED_DOT_COUNT) if mask & (1 << n)]
        return cls(tuple(dots))

    @classmethod
    def from_unicode(cls, char: str) -> "BrailleCell":
        """Build a cell from a Unicode braille character."""
        if not char or len(char) != 1:
            raise BrailleError("يجب تمرير محرف واحد فقط لتحويله إلى خلية برايل")
        code = ord(char)
        if not BRAILLE_UNICODE_BASE <= code <= BRAILLE_UNICODE_MAX:
            raise BrailleError(f"المحرف {char!r} ليس من محارف برايل في يونيكود")
        return cls.from_bitmask(code - BRAILLE_UNICODE_BASE)

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------
    def to_dot_string(self, separator: str = "-") -> str:
        """Return the dots as ``"1-4-5"``; empty cells return ``""``."""
        return separator.join(str(d) for d in self.dots)

    def to_bitmask(self) -> int:
        """Return the classic 6/8 dot bit mask."""
        mask = 0
        for dot in self.dots:
            mask |= 1 << (dot - 1)
        return mask

    def to_unicode(self) -> str:
        """Return the Unicode braille pattern character for this cell."""
        return chr(BRAILLE_UNICODE_BASE + self.to_bitmask())

    # ------------------------------------------------------------------
    # Inspection
    # ------------------------------------------------------------------
    @property
    def is_empty(self) -> bool:
        return not self.dots

    @property
    def count(self) -> int:
        return len(self.dots)

    def has(self, dot: int) -> bool:
        return dot in self.dots

    def with_dot(self, dot: int) -> "BrailleCell":
        """Return a new cell with ``dot`` toggled on."""
        return BrailleCell.from_dots((*self.dots, dot))

    def without_dot(self, dot: int) -> "BrailleCell":
        """Return a new cell with ``dot`` toggled off."""
        return BrailleCell.from_dots(d for d in self.dots if d != dot)

    def toggle(self, dot: int) -> "BrailleCell":
        """Return a new cell with ``dot`` toggled."""
        return self.without_dot(dot) if self.has(dot) else self.with_dot(dot)

    def describe_ar(self) -> str:
        """Human readable Arabic description, useful for screen readers."""
        if self.is_empty:
            return "لا توجد نقاط محددة"
        names = [DOT_NAMES_AR[d] for d in self.dots]
        return "، ".join(names)

    def describe_numeric_ar(self) -> str:
        """Compact Arabic description, e.g. ``"النقاط: 1، 4، 5"``."""
        if self.is_empty:
            return "لا توجد نقاط محددة"
        return "النقاط: " + "، ".join(str(d) for d in self.dots)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.to_unicode()


def normalise_cell(cell: BrailleCell | str | Sequence[int]) -> BrailleCell:
    """Coerce several representations into a :class:`BrailleCell`."""
    if isinstance(cell, BrailleCell):
        return cell
    if isinstance(cell, str):
        return BrailleCell.from_dot_string(cell)
    return BrailleCell.from_dots(cell)


def cells_to_unicode(cells: Iterable[BrailleCell]) -> str:
    """Render a sequence of cells as one Unicode braille string."""
    return "".join(cell.to_unicode() for cell in cells)


def unicode_to_cells(text: str) -> list[BrailleCell]:
    """Split a Unicode braille string into a list of cells.

    Non-braille characters are ignored so that mixed strings degrade
    gracefully instead of raising.
    """
    result: list[BrailleCell] = []
    for char in text or "":
        code = ord(char)
        if BRAILLE_UNICODE_BASE <= code <= BRAILLE_UNICODE_MAX:
            result.append(BrailleCell.from_bitmask(code - BRAILLE_UNICODE_BASE))
    return result


def dots_to_bitmask(dots: Iterable[int]) -> int:
    """Return the bit mask for an iterable of dots."""
    return BrailleCell.from_dots(dots).to_bitmask()


def bitmask_to_dots(mask: int) -> tuple[int, ...]:
    """Return the dots encoded in ``mask``."""
    return BrailleCell.from_bitmask(mask).dots


def dots_to_unicode(dots: Iterable[int]) -> str:
    """Return the Unicode braille character for a set of dots."""
    return BrailleCell.from_dots(dots).to_unicode()


def unicode_to_dots(char: str) -> tuple[int, ...]:
    """Return the dots encoded in a Unicode braille character."""
    return BrailleCell.from_unicode(char).dots


def differing_dots(a: BrailleCell, b: BrailleCell) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return ``(missing, extra)`` dots needed to turn ``a`` into ``b``."""
    a_dots, b_dots = set(a.dots), set(b.dots)
    missing = tuple(sorted(b_dots - a_dots))
    extra = tuple(sorted(a_dots - b_dots))
    return missing, extra


def describe_difference_ar(a: BrailleCell, b: BrailleCell) -> str:
    """Explain in simple Arabic how ``a`` differs from the expected cell ``b``."""
    missing, extra = differing_dots(a, b)
    parts: list[str] = []
    if missing:
        parts.append("نقاط ناقصة: " + "، ".join(str(d) for d in missing))
    if extra:
        parts.append("نقاط زائدة: " + "، ".join(str(d) for d in extra))
    if not parts:
        return "الأنماط متطابقة"
    return "، ".join(parts)
