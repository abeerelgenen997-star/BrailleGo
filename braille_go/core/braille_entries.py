"""هياكل البيانات الخام لرموز برايل.

The data modules deliberately use tiny, dependency-free records so that the
braille tables can be read, reviewed and corrected in isolation.  The records
are converted into :class:`braille_go.core.symbols.BrailleSymbol` objects by
``build_default_repository``.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SymbolEntry:
    """رمز برايل من خلية واحدة.

    ``dots`` is a compact string such as ``"145"`` or ``""`` for the space.
    """

    key: str
    char: str
    dots: str
    name_ar: str
    name_en: str = ""
    notes_ar: str = ""


@dataclass(frozen=True)
class MultiCellEntry:
    """رمز برايل مكوّن من أكثر من خلية (أو رمز بعلامة بادئة).

    ``dots`` is a tuple of compact dot strings, one per cell.
    """

    key: str
    char: str
    dots: tuple[str, ...]
    name_ar: str
    name_en: str = ""
    notes_ar: str = ""
    language: str = "ar"
    tags: tuple[str, ...] = field(default_factory=tuple)
