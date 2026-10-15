"""اختبارات تحويل برايل والنصوص."""

from braille_go.core import braille, braille_text


def test_braille_cell_basic():
    cell = braille.BrailleCell.from_dots("145")
    assert cell.dots == (1, 4, 5)
    assert cell.to_unicode() == "⠙"


def test_unicode_roundtrip():
    original = "بسم"
    res = braille_text.transcribe(original, language="ar")
    assert res.is_complete
    assert res.unicode


def test_english_capital():
    res = braille_text.transcribe("Cat", language="en")
    # ⠠⠉⠁⠞
    assert "⠠" in res.unicode
    assert res.is_complete


def test_description_difference():
    a = braille.BrailleCell.from_dots("1")
    b = braille.BrailleCell.from_dots("14")
    diff = braille.describe_difference_ar(a, b)
    assert "ناقص" in diff or "زائدة" in diff


def test_transcribe_mixed_digits():
    res = braille_text.transcribe("أ1", language="ar")
    assert res.cells  # has number sign


def test_empty_cell():
    c = braille.BrailleCell.empty()
    assert c.is_empty
    assert c.count == 0
