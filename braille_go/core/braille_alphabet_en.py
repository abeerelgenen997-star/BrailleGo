"""الحروف الإنجليزية بطريقة برايل (الدرجة الأولى / الحروف المفردة).

المصدر: جدول برايل الإنجليزي/الدولي (انظر BRAILLE_DATA_SOURCES.md).
هذه هي الدرجة الأولى غير المختصرة (Grade 1)، وهي المدخل المناسب للمبتدئ.
الحروف الكبيرة تُكتب بعد علامة الحرف الكبير ⠠ (النقطة 6).
"""

from __future__ import annotations

from .braille_entries import SymbolEntry

#: الحروف الإنجليزية الصغيرة.
ENGLISH_LETTERS: tuple[SymbolEntry, ...] = (
    SymbolEntry("en_a", "a", "1", "A", "a"),
    SymbolEntry("en_b", "b", "12", "B", "b"),
    SymbolEntry("en_c", "c", "14", "C", "c"),
    SymbolEntry("en_d", "d", "145", "D", "d"),
    SymbolEntry("en_e", "e", "15", "E", "e"),
    SymbolEntry("en_f", "f", "124", "F", "f"),
    SymbolEntry("en_g", "g", "1245", "G", "g"),
    SymbolEntry("en_h", "h", "125", "H", "h"),
    SymbolEntry("en_i", "i", "24", "I", "i"),
    SymbolEntry("en_j", "j", "245", "J", "j"),
    SymbolEntry("en_k", "k", "13", "K", "k"),
    SymbolEntry("en_l", "l", "123", "L", "l"),
    SymbolEntry("en_m", "m", "134", "M", "m"),
    SymbolEntry("en_n", "n", "1345", "N", "n"),
    SymbolEntry("en_o", "o", "135", "O", "o"),
    SymbolEntry("en_p", "p", "1234", "P", "p"),
    SymbolEntry("en_q", "q", "12345", "Q", "q"),
    SymbolEntry("en_r", "r", "1235", "R", "r"),
    SymbolEntry("en_s", "s", "234", "S", "s"),
    SymbolEntry("en_t", "t", "2345", "T", "t"),
    SymbolEntry("en_u", "u", "136", "U", "u"),
    SymbolEntry("en_v", "v", "1236", "V", "v"),
    SymbolEntry("en_w", "w", "2456", "W", "w"),
    SymbolEntry("en_x", "x", "1346", "X", "x"),
    SymbolEntry("en_y", "y", "13456", "Y", "y"),
    SymbolEntry("en_z", "z", "1356", "Z", "z"),
)

#: علامة الحرف الكبير في برايل الإنجليزي (النقطة 6).
CAPITAL_SIGN_DOTS = "6"
