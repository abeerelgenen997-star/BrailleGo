"""المنهج التعليمي: المستويات والدروس وربطها برموز برايل.

The curriculum is deliberately *data driven*: adding a lesson or a whole level
means appending a :class:`Level` object here, with no changes to the GUI, the
database schema or the exercise engine.  Levels are ordered and each lesson
declares which braille symbol keys it teaches plus which exercise kinds are
appropriate, which is everything the exercise generator needs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .exercise_types import ExerciseKind


@dataclass(frozen=True)
class Lesson:
    """درس واحد داخل مستوى."""

    key: str
    title_ar: str
    description_ar: str = ""
    symbol_keys: tuple[str, ...] = ()
    exercise_kinds: tuple[ExerciseKind, ...] = (ExerciseKind.IDENTIFY_CHAR,)
    intro_ar: str = ""
    words: tuple[str, ...] = ()
    sentences: tuple[str, ...] = ()
    language: str = "ar"
    is_exam: bool = False
    exercise_count: int = 8
    #: أزواج من المفاتيح للتدريب على التمييز بين الرموز المتشابهة.
    discrimination_pairs: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Level:
    """مستوى تعليمي متكامل."""

    number: int
    key: str
    title_ar: str
    description_ar: str
    lessons: tuple[Lesson, ...] = field(default_factory=tuple)

    @property
    def lesson_keys(self) -> tuple[str, ...]:
        return tuple(lesson.key for lesson in self.lessons)

    def lesson(self, key: str) -> Lesson | None:
        for lesson in self.lessons:
            if lesson.key == key:
                return lesson
        return None

    @property
    def is_exam_only(self) -> bool:
        return bool(self.lessons) and all(lesson.is_exam for lesson in self.lessons)


_AR_BASIC_A = (
    "ar_alif", "ar_ba", "ar_ta", "ar_tha", "ar_jeem",
    "ar_hha", "ar_kha", "ar_dal", "ar_thal", "ar_ra",
)
_AR_BASIC_B = (
    "ar_zay", "ar_seen", "ar_sheen", "ar_sad", "ar_dad",
    "ar_taa", "ar_zha", "ar_ain", "ar_ghain", "ar_fa",
)
_AR_BASIC_C = (
    "ar_qaf", "ar_kaf", "ar_lam", "ar_meem",
    "ar_noon", "ar_ha", "ar_waw", "ar_ya",
)
_AR_EXTENDED = (
    "ar_alef_maksura", "ar_ta_marbuta", "ar_hamza",
    "ar_alef_hamza_above", "ar_alef_hamza_below",
    "ar_alef_madda", "ar_waw_hamza", "ar_ya_hamza",
)
_AR_LIGATURES = ("ar_lig_al_lam", "ar_lig_lam_alef", "ar_lig_aw")

_EN_GROUP_1 = tuple(f"en_{c}" for c in "abcdefghi")
_EN_GROUP_2 = tuple(f"en_{c}" for c in "jklmnopqr")
_EN_GROUP_3 = tuple(f"en_{c}" for c in "stuvwxyz")

_ARABIC_WORDS = (
    "باب", "بيت", "نور", "علم", "قلم", "شمس", "قمر",
    "كتاب", "سلام", "ولد", "درس", "ماء",
)
_ARABIC_SENTENCES = (
    "السلام عليكم",
    "هذا كتاب",
    "البيت كبير",
    "أنا أتعلم برايل",
    "القلم على المكتب",
)
_ENGLISH_WORDS = (
    "cat", "dog", "sun", "moon", "book", "pen", "hat",
    "bus", "red", "big", "man", "map",
)
_ENGLISH_SENTENCES = (
    "I can read",
    "The sun is hot",
    "This is a book",
    "We learn braille",
)

#: أزواج متشابهة يستخدمها درس التمييز.
_SIMILAR_PAIRS: tuple[tuple[str, str], ...] = (
    ("ar_alif", "ar_ba"),
    ("ar_ba", "ar_kaf"),
    ("ar_ta", "ar_taa"),
    ("ar_jeem", "ar_ya"),
    ("ar_meem", "ar_noon"),
    ("ar_sheen", "ar_dad"),
    ("ar_ra", "ar_zay"),
    ("ar_ha", "ar_alif"),          # 125 مقابل 1
    ("dia_fatha", "dia_fathatan"),
    ("dia_damma", "dia_kasra"),
    ("punct_en_period", "punct_en_question"),
    ("sym_number_sign", "punct_en_asterisk"),
)

LEVELS: tuple[Level, ...] = (
    # ------------------------------------------------------------------
    Level(
        number=1,
        key="level_intro",
        title_ar="المستوى 1: مقدمة إلى طريقة برايل",
        description_ar="تعرّف على طريقة برايل وخلية النقاط الست وترتيب النقاط.",
        lessons=(
            Lesson(
                key="l1_what_is_braille",
                title_ar="ما هي طريقة برايل؟",
                description_ar="فكرة مبسطة عن برايل وكيف تُقرأ بالنقاط البارزة.",
                exercise_kinds=(ExerciseKind.BUILD_FROM_DESCRIPTION,),
                intro_ar=(
                    "طريقة برايل نظام كتابة وقراءة يعتمد على نقاط بارزة تشعر بها بأطراف "
                    "الأصابع. تُقرأ برايل من اليسار إلى اليمين، وتتكوّن الوحدة الأساسية من "
                    "خلية تضم ستّ نقاط مرتّبة في عمودين وثلاثة صفوف:\n"
                    "النقطة 1 والنقطة 4 في الأعلى، ثم 2 و5 في الوسط، ثم 3 و6 في الأسفل.\n"
                    "كل حرف أو رقم أو علامة برايل هو مجموعة مختلفة من هذه النقاط الست."
                ),
                exercise_count=6,
            ),
            Lesson(
                key="l1_cell_layout",
                title_ar="خلية برايل وترتيب النقاط",
                description_ar="تعرّف على مواقع النقاط الست داخل الخلية.",
                exercise_kinds=(ExerciseKind.BUILD_FROM_DESCRIPTION,),
                intro_ar=(
                    "العمود الأيمن في الخلية يضمّ النقاط 4 و5 و6، والعمود الأيسر يضمّ "
                    "النقاط 1 و2 و3. عندما نسمّي النقاط نذكرها دائمًا بترتيب تصاعدي: "
                    "1 ثم 2 ثم 3 ثم 4 ثم 5 ثم 6."
                ),
                exercise_count=8,
            ),
            Lesson(
                key="l1_dot_practice",
                title_ar="تدريب على تحديد النقاط",
                description_ar="تدرّب على تمييز مواقع النقاط واختيارها.",
                exercise_kinds=(ExerciseKind.BUILD_FROM_DESCRIPTION,),
                exercise_count=8,
            ),
            Lesson(
                key="l1_exam",
                title_ar="اختبار المستوى الأول",
                description_ar="اختبار قصير على مفاهيم الخلية والنقاط.",
                exercise_kinds=(
                    ExerciseKind.BUILD_FROM_DESCRIPTION,
                    ExerciseKind.IDENTIFY_PATTERN,
                ),
                is_exam=True,
                exercise_count=8,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=2,
        key="level_ar_1",
        title_ar="المستوى 2: الحروف العربية (المجموعة الأولى)",
        description_ar="تعلّم عشرة حروف عربية أساسية وتمييزها.",
        lessons=(
            Lesson(
                key="l2_letters_a",
                title_ar="الحروف: ا، ب، ت، ث، ج",
                description_ar="أول خمسة حروف عربية بطريقة برايل.",
                symbol_keys=("ar_alif", "ar_ba", "ar_ta", "ar_tha", "ar_jeem"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l2_letters_b",
                title_ar="الحروف: ح، خ، د، ذ، ر",
                description_ar="خمسة حروف جديدة مع مراجعة ما سبق.",
                symbol_keys=("ar_hha", "ar_kha", "ar_dal", "ar_thal", "ar_ra"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l2_review",
                title_ar="مراجعة الحروف العشرة",
                description_ar="تدريب شامل على المجموعة الأولى.",
                symbol_keys=_AR_BASIC_A,
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.DISCRIMINATE,
                ),
                discrimination_pairs=_SIMILAR_PAIRS[:2],
                exercise_count=10,
            ),
            Lesson(
                key="l2_exam",
                title_ar="اختبار المستوى الثاني",
                description_ar="اختبار على الحروف العربية في المجموعة الأولى.",
                symbol_keys=_AR_BASIC_A,
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                ),
                is_exam=True,
                exercise_count=10,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=3,
        key="level_ar_2",
        title_ar="المستوى 3: بقية الحروف العربية",
        description_ar="أكمل الحروف العربية والهمزات والتراكيب الشائعة.",
        lessons=(
            Lesson(
                key="l3_letters_a",
                title_ar="الحروف: ز، س، ش، ص، ض",
                symbol_keys=("ar_zay", "ar_seen", "ar_sheen", "ar_sad", "ar_dad"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l3_letters_b",
                title_ar="الحروف: ط، ظ، ع، غ، ف",
                symbol_keys=("ar_taa", "ar_zha", "ar_ain", "ar_ghain", "ar_fa"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l3_letters_c",
                title_ar="الحروف: ق، ك، ل، م، ن، ه، و، ي",
                symbol_keys=_AR_BASIC_C,
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=12,
            ),
            Lesson(
                key="l3_extended",
                title_ar="الألف المقصورة والهمزات والتراكيب",
                symbol_keys=_AR_EXTENDED + _AR_LIGATURES,
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.DISCRIMINATE,
                ),
                discrimination_pairs=(("ar_alif", "ar_alef_hamza_above"),),
                exercise_count=10,
            ),
            Lesson(
                key="l3_exam",
                title_ar="اختبار المستوى الثالث",
                symbol_keys=_AR_BASIC_B + _AR_BASIC_C,
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                ),
                is_exam=True,
                exercise_count=12,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=4,
        key="level_en",
        title_ar="المستوى 4: الحروف الإنجليزية",
        description_ar="تعلّم الحروف الإنجليزية (الدرجة الأولى) وعلامة الحرف الكبير.",
        lessons=(
            Lesson(
                key="l4_en_a",
                title_ar="الحروف الإنجليزية: a–i",
                symbol_keys=_EN_GROUP_1,
                language="en",
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l4_en_b",
                title_ar="الحروف الإنجليزية: j–r",
                symbol_keys=_EN_GROUP_2,
                language="en",
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l4_en_c",
                title_ar="الحروف الإنجليزية: s–z",
                symbol_keys=_EN_GROUP_3,
                language="en",
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.TYPE_ANSWER,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l4_en_caps",
                title_ar="علامة الحرف الكبير",
                description_ar="تعرّف على علامة الحرف الكبير ⠠ وموضعها.",
                symbol_keys=("sym_capital_sign", *_EN_GROUP_1),
                language="en",
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.TYPE_ANSWER),
                exercise_count=8,
            ),
            Lesson(
                key="l4_exam",
                title_ar="اختبار المستوى الرابع",
                symbol_keys=_EN_GROUP_1 + _EN_GROUP_2 + _EN_GROUP_3,
                language="en",
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.BUILD_PATTERN,
                ),
                is_exam=True,
                exercise_count=12,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=5,
        key="level_digits",
        title_ar="المستوى 5: الأرقام",
        description_ar="تعلّم الأرقام وعلامة الرقم وترتيب كتابتها.",
        lessons=(
            Lesson(
                key="l5_digits_sign",
                title_ar="علامة الرقم والأرقام 1–5",
                symbol_keys=("sym_number_sign", "digit_1", "digit_2", "digit_3",
                             "digit_4", "digit_5"),
                exercise_kinds=(
                    ExerciseKind.NUMBER_EXERCISE,
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.BUILD_PATTERN,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l5_digits_b",
                title_ar="الأرقام 6–9 والصفر",
                symbol_keys=("digit_6", "digit_7", "digit_8", "digit_9", "digit_0"),
                exercise_kinds=(
                    ExerciseKind.NUMBER_EXERCISE,
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.BUILD_PATTERN,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l5_exam",
                title_ar="اختبار المستوى الخامس",
                symbol_keys=("sym_number_sign", *(f"digit_{i}" for i in range(1, 10)), "digit_0"),
                exercise_kinds=(ExerciseKind.NUMBER_EXERCISE, ExerciseKind.IDENTIFY_CHAR),
                is_exam=True,
                exercise_count=10,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=6,
        key="level_punctuation",
        title_ar="المستوى 6: علامات الترقيم",
        description_ar="تعلّم علامات الترقيم العربية والإنجليزية ومواضعها.",
        lessons=(
            Lesson(
                key="l6_punct_ar",
                title_ar="الترقيم العربي المشترك",
                symbol_keys=("punct_ar_comma", "punct_ar_semicolon", "punct_ar_colon",
                             "punct_ar_period", "punct_ar_exclamation",
                             "punct_ar_question", "punct_ar_hyphen"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.PUNCTUATION_EXERCISE,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l6_punct_en",
                title_ar="الترقيم الإنجليزي",
                symbol_keys=("punct_en_comma", "punct_en_semicolon", "punct_en_colon",
                             "punct_en_period", "punct_en_exclamation",
                             "punct_en_question", "punct_en_apostrophe"),
                language="en",
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.PUNCTUATION_EXERCISE,
                ),
                exercise_count=10,
            ),
            Lesson(
                key="l6_punct_marks",
                title_ar="الأقواس وعلامات التنصيص",
                description_ar="تعرّف على الفرق بين أنظمة الترقيم.",
                symbol_keys=("punct_ar_u_quote", "punct_ar_u_paren", "punct_ar_u_bracket",
                             "punct_en_quote_open", "punct_en_paren_open", "punct_en_slash"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.PUNCTUATION_EXERCISE),
                exercise_count=8,
            ),
            Lesson(
                key="l6_exam",
                title_ar="اختبار المستوى السادس",
                symbol_keys=("punct_ar_comma", "punct_ar_semicolon", "punct_ar_colon",
                             "punct_ar_period", "punct_ar_exclamation",
                             "punct_ar_question", "punct_ar_hyphen"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.PUNCTUATION_EXERCISE),
                is_exam=True,
                exercise_count=10,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=7,
        key="level_diacritics",
        title_ar="المستوى 7: التشكيل العربي",
        description_ar="تعلّم الحركات والشدّة والسكون ومواضعها في برايل.",
        lessons=(
            Lesson(
                key="l7_harakat",
                title_ar="الفتحة والضمة والكسرة",
                symbol_keys=("dia_fatha", "dia_damma", "dia_kasra"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.BUILD_PATTERN,
                    ExerciseKind.DISCRIMINATE,
                ),
                discrimination_pairs=(("dia_damma", "dia_kasra"),),
                exercise_count=8,
            ),
            Lesson(
                key="l7_tanween",
                title_ar="التنوين",
                symbol_keys=("dia_fathatan", "dia_dammatan", "dia_kasratan"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.BUILD_PATTERN),
                exercise_count=8,
            ),
            Lesson(
                key="l7_sukun_shadda",
                title_ar="السكون والشدّة",
                symbol_keys=("dia_sukun", "dia_shadda"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.BUILD_PATTERN),
                exercise_count=8,
            ),
            Lesson(
                key="l7_exam",
                title_ar="اختبار المستوى السابع",
                symbol_keys=("dia_fatha", "dia_damma", "dia_kasra", "dia_fathatan",
                             "dia_dammatan", "dia_kasratan", "dia_sukun", "dia_shadda"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.DISCRIMINATE),
                is_exam=True,
                exercise_count=10,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=8,
        key="level_symbols",
        title_ar="المستوى 8: الرموز والعلامات الشائعة",
        description_ar="تعرّف على علامات الرقم والحرف الكبير والاختصار والفراغ.",
        lessons=(
            Lesson(
                key="l8_marks",
                title_ar="علامات الرقم والحرف الكبير والتأكيد",
                symbol_keys=("sym_number_sign", "sym_capital_sign", "sym_emphasis",
                             "sym_decimal_point"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.IDENTIFY_PATTERN),
                exercise_count=8,
            ),
            Lesson(
                key="l8_other",
                title_ar="رموز أخرى",
                symbol_keys=("sym_space", "sym_abbreviation", "sym_contraction_prefix",
                             "punct_en_asterisk", "punct_en_ampersand", "punct_en_at"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.BUILD_PATTERN),
                exercise_count=8,
            ),
            Lesson(
                key="l8_exam",
                title_ar="اختبار المستوى الثامن",
                symbol_keys=("sym_number_sign", "sym_capital_sign", "sym_emphasis",
                             "sym_decimal_point", "sym_abbreviation", "punct_en_at"),
                exercise_kinds=(ExerciseKind.IDENTIFY_CHAR, ExerciseKind.IDENTIFY_PATTERN),
                is_exam=True,
                exercise_count=8,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=9,
        key="level_words",
        title_ar="المستوى 9: تكوين الكلمات",
        description_ar="كوّن كلمات عربية وإنجليزية باستخدام خلايا برايل.",
        lessons=(
            Lesson(
                key="l9_words_ar",
                title_ar="تكوين كلمات عربية",
                symbol_keys=_AR_BASIC_A + _AR_BASIC_C[:3],
                words=_ARABIC_WORDS[:8],
                exercise_kinds=(ExerciseKind.BUILD_WORD, ExerciseKind.READ_WORD),
                exercise_count=8,
            ),
            Lesson(
                key="l9_words_en",
                title_ar="تكوين كلمات إنجليزية",
                symbol_keys=_EN_GROUP_1 + _EN_GROUP_2 + _EN_GROUP_3,
                language="en",
                words=_ENGLISH_WORDS,
                exercise_kinds=(ExerciseKind.BUILD_WORD, ExerciseKind.READ_WORD),
                exercise_count=8,
            ),
            Lesson(
                key="l9_exam",
                title_ar="اختبار المستوى التاسع",
                symbol_keys=_AR_BASIC_A + _AR_BASIC_C,
                words=_ARABIC_WORDS,
                language="ar",
                exercise_kinds=(ExerciseKind.BUILD_WORD, ExerciseKind.READ_WORD),
                is_exam=True,
                exercise_count=10,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=10,
        key="level_sentences",
        title_ar="المستوى 10: قراءة الكلمات والجمل",
        description_ar="اقرأ جملًا كاملة مكتوبة بطريقة برايل واحكم على معناها.",
        lessons=(
            Lesson(
                key="l10_sentences_ar",
                title_ar="قراءة جمل عربية",
                symbol_keys=_AR_BASIC_A,
                sentences=_ARABIC_SENTENCES,
                exercise_kinds=(ExerciseKind.READ_SENTENCE, ExerciseKind.READ_WORD),
                exercise_count=8,
            ),
            Lesson(
                key="l10_sentences_en",
                title_ar="قراءة جمل إنجليزية",
                symbol_keys=_EN_GROUP_1 + _EN_GROUP_2,
                language="en",
                sentences=_ENGLISH_SENTENCES,
                exercise_kinds=(ExerciseKind.READ_SENTENCE, ExerciseKind.READ_WORD),
                exercise_count=8,
            ),
            Lesson(
                key="l10_exam",
                title_ar="اختبار المستوى العاشر",
                symbol_keys=_AR_BASIC_A,
                sentences=_ARABIC_SENTENCES,
                exercise_kinds=(ExerciseKind.READ_SENTENCE,),
                is_exam=True,
                exercise_count=8,
            ),
        ),
    ),
    # ------------------------------------------------------------------
    Level(
        number=11,
        key="level_discrimination",
        title_ar="المستوى 11: التمييز بين الرموز المتشابهة",
        description_ar="تدرّب على تمييز الرموز المتشابهة التي يسهل الخلط بينها.",
        lessons=(
            Lesson(
                key="l11_similar_ar",
                title_ar="رموز عربية متشابهة",
                symbol_keys=("ar_alif", "ar_ba", "ar_kaf", "ar_ta", "ar_taa",
                             "ar_jeem", "ar_ya", "ar_meem", "ar_noon", "ar_sheen", "ar_dad"),
                exercise_kinds=(ExerciseKind.DISCRIMINATE, ExerciseKind.IDENTIFY_CHAR),
                discrimination_pairs=_SIMILAR_PAIRS[:7],
                exercise_count=10,
            ),
            Lesson(
                key="l11_similar_marks",
                title_ar="علامات متشابهة",
                symbol_keys=("dia_fatha", "dia_fathatan", "dia_damma", "dia_kasra",
                             "punct_en_period", "punct_en_question"),
                exercise_kinds=(ExerciseKind.DISCRIMINATE, ExerciseKind.IDENTIFY_CHAR),
                discrimination_pairs=_SIMILAR_PAIRS[7:],
                exercise_count=10,
            ),
            Lesson(
                key="l11_exam",
                title_ar="الاختبار الشامل النهائي",
                description_ar="اختبار شامل يجمع الحروف والأرقام والترقيم والرموز.",
                symbol_keys=("ar_alif", "ar_ba", "ar_ta", "ar_ya", "ar_meem", "ar_noon",
                             "en_a", "en_b", "en_c", "digit_1", "digit_2",
                             "punct_ar_comma", "dia_fatha", "sym_number_sign"),
                exercise_kinds=(
                    ExerciseKind.IDENTIFY_CHAR,
                    ExerciseKind.IDENTIFY_PATTERN,
                    ExerciseKind.DISCRIMINATE,
                    ExerciseKind.NUMBER_EXERCISE,
                ),
                discrimination_pairs=_SIMILAR_PAIRS,
                is_exam=True,
                exercise_count=15,
            ),
        ),
    ),
)

#: فهرس سريع: مفتاح المستوى -> المستوى.
LEVELS_BY_KEY: dict[str, Level] = {level.key: level for level in LEVELS}

#: فهرس سريع: مفتاح الدرس -> الدرس.
LESSONS_BY_KEY: dict[str, Lesson] = {
    lesson.key: lesson for level in LEVELS for lesson in level.lessons
}

# ----------------------------------------------------------------------
# الترجمة الإنجليزية للمستويات والدروس
# ----------------------------------------------------------------------
# الواجهة تدعم العربية والإنجليزية والفرنسية والإسبانية، ولأن عناوين المنهج
# مُعرّفة بالعربية داخل البيانات نضيف هنا الترجمة الإنجليزية لكل مستوى ودرس،
# وتُستخدم الإنجليزية بديلًا للفرنسية والإسبانية حتى تكتمل ترجمتها لاحقًا.
# اختبار الوحدة يتحقّق من وجود ترجمة إنجليزية لكل مفتاح حتى لا تتسرّب عناوين
# عربية إلى واجهة غير عربية.

_LEVEL_TITLES_EN: dict[str, str] = {
    "level_intro": "Level 1: Introduction to Braille",
    "level_ar_1": "Level 2: Arabic Letters (Group 1)",
    "level_ar_2": "Level 3: The Rest of the Arabic Letters",
    "level_en": "Level 4: English Letters",
    "level_digits": "Level 5: Numbers",
    "level_punctuation": "Level 6: Punctuation",
    "level_diacritics": "Level 7: Arabic Diacritics",
    "level_symbols": "Level 8: Common Signs and Symbols",
    "level_words": "Level 9: Building Words",
    "level_sentences": "Level 10: Reading Words and Sentences",
    "level_discrimination": "Level 11: Telling Similar Symbols Apart",
}

_LEVEL_DESCRIPTIONS_EN: dict[str, str] = {
    "level_intro": "Get to know braille, the six-dot cell and the order of the dots.",
    "level_ar_1": "Learn ten basic Arabic letters and tell them apart.",
    "level_ar_2": "Complete the Arabic letters, the hamzas and the common ligatures.",
    "level_en": "Learn the English letters (Grade 1) and the capital sign.",
    "level_digits": "Learn the numbers, the number sign and how they are written.",
    "level_punctuation": "Learn Arabic and English punctuation and their positions.",
    "level_diacritics": "Learn the short vowels, the shadda and the sukun and their positions in braille.",
    "level_symbols": "Learn the number sign, the capital sign, the abbreviation and the space signs.",
    "level_words": "Build Arabic and English words using braille cells.",
    "level_sentences": "Read full sentences written in braille and understand their meaning.",
    "level_discrimination": "Practise telling apart symbols that are easy to confuse.",
}

_LESSON_TITLES_EN: dict[str, str] = {
    # المستوى 1
    "l1_what_is_braille": "What is Braille?",
    "l1_cell_layout": "The Braille Cell and the Order of the Dots",
    "l1_dot_practice": "Dot Identification Practice",
    "l1_exam": "Level 1 Exam",
    # المستوى 2
    "l2_letters_a": "Letters: alif, ba, ta, tha, jeem",
    "l2_letters_b": "Letters: hha, kha, dal, thal, ra",
    "l2_review": "Review of the Ten Letters",
    "l2_exam": "Level 2 Exam",
    # المستوى 3
    "l3_letters_a": "Letters: zay, seen, sheen, sad, dad",
    "l3_letters_b": "Letters: taa, zha, ain, ghain, fa",
    "l3_letters_c": "Letters: qaf, kaf, lam, meem, noon, ha, waw, ya",
    "l3_extended": "Alif Maqsura, Hamzas and Ligatures",
    "l3_exam": "Level 3 Exam",
    # المستوى 4
    "l4_en_a": "English Letters: a–i",
    "l4_en_b": "English Letters: j–r",
    "l4_en_c": "English Letters: s–z",
    "l4_en_caps": "The Capital Sign",
    "l4_exam": "Level 4 Exam",
    # المستوى 5
    "l5_digits_sign": "The Number Sign and Digits 1–5",
    "l5_digits_b": "Digits 6–9 and Zero",
    "l5_exam": "Level 5 Exam",
    # المستوى 6
    "l6_punct_ar": "Common Arabic Punctuation",
    "l6_punct_en": "English Punctuation",
    "l6_punct_marks": "Brackets and Quotation Marks",
    "l6_exam": "Level 6 Exam",
    # المستوى 7
    "l7_harakat": "Fatha, Damma and Kasra",
    "l7_tanween": "Tanween (Double Vowels)",
    "l7_sukun_shadda": "Sukun and Shadda",
    "l7_exam": "Level 7 Exam",
    # المستوى 8
    "l8_marks": "Number, Capital and Emphasis Signs",
    "l8_other": "Other Symbols",
    "l8_exam": "Level 8 Exam",
    # المستوى 9
    "l9_words_ar": "Building Arabic Words",
    "l9_words_en": "Building English Words",
    "l9_exam": "Level 9 Exam",
    # المستوى 10
    "l10_sentences_ar": "Reading Arabic Sentences",
    "l10_sentences_en": "Reading English Sentences",
    "l10_exam": "Level 10 Exam",
    # المستوى 11
    "l11_similar_ar": "Similar Arabic Symbols",
    "l11_similar_marks": "Similar Signs",
    "l11_exam": "Final Comprehensive Exam",
}

_LESSON_DESCRIPTIONS_EN: dict[str, str] = {
    "l1_what_is_braille": "A simple idea of braille and how it is read through raised dots.",
    "l1_cell_layout": "Learn the positions of the six dots inside the cell.",
    "l1_dot_practice": "Practise recognising and selecting dot positions.",
    "l1_exam": "A short exam on the cell and dot concepts.",
    "l2_letters_a": "The first five Arabic letters in braille.",
    "l2_letters_b": "Five new letters with a review of the previous ones.",
    "l2_review": "A comprehensive practice on the first group.",
    "l2_exam": "An exam on the Arabic letters of the first group.",
    "l4_en_caps": "Learn the capital sign ⠠ and its position.",
    "l6_punct_marks": "Learn the difference between the punctuation systems.",
    "l11_exam": "A comprehensive exam combining letters, numbers, punctuation and symbols.",
}

_LESSON_INTROS_EN: dict[str, str] = {
    "l1_what_is_braille": (
        "Braille is a reading and writing system based on raised dots that you "
        "feel with your fingertips. Braille is read from left to right, and its "
        "basic unit is a cell of six dots arranged in two columns and three "
        "rows:\nDot 1 and dot 4 at the top, then 2 and 5 in the middle, then 3 "
        "and 6 at the bottom.\nEvery letter, number or sign is a different "
        "combination of these six dots."
    ),
    "l1_cell_layout": (
        "The right column of the cell holds dots 4, 5 and 6, and the left "
        "column holds dots 1, 2 and 3. When we name dots we always list them in "
        "ascending order: 1, then 2, then 3, then 4, then 5, then 6."
    ),
}


def level_title(level: Level, language: str = "ar") -> str:
    """عنوان المستوى بحسب لغة الواجهة (الإنجليزية بديلًا لغير العربية)."""
    if language == "ar":
        return level.title_ar
    return _LEVEL_TITLES_EN.get(level.key, level.title_ar)


def level_description(level: Level, language: str = "ar") -> str:
    """وصف المستوى بحسب لغة الواجهة."""
    if language == "ar":
        return level.description_ar
    return _LEVEL_DESCRIPTIONS_EN.get(level.key, level.description_ar or level.title_ar)


def lesson_title(lesson: Lesson, language: str = "ar") -> str:
    """عنوان الدرس بحسب لغة الواجهة."""
    if language == "ar":
        return lesson.title_ar
    return _LESSON_TITLES_EN.get(lesson.key, lesson.title_ar)


def lesson_description(lesson: Lesson, language: str = "ar") -> str:
    """وصف الدرس بحسب لغة الواجهة."""
    if language == "ar":
        return lesson.description_ar
    return (
        _LESSON_DESCRIPTIONS_EN.get(lesson.key)
        or lesson.description_ar
        or _LESSON_TITLES_EN.get(lesson.key, lesson.title_ar)
    )


def lesson_intro(lesson: Lesson, language: str = "ar") -> str:
    """المقدمة التعليمية للدرس بحسب لغة الواجهة."""
    if language == "ar":
        return lesson.intro_ar
    return _LESSON_INTROS_EN.get(lesson.key, lesson.intro_ar)


def level_of_lesson(lesson_key: str) -> Level | None:
    """أعد المستوى الذي ينتمي إليه الدرس."""
    for level in LEVELS:
        if lesson_key in level.lesson_keys:
            return level
    return None


def next_lesson(lesson_key: str) -> Lesson | None:
    """أعد الدرس التالي في الترتيب العام (عبر كل المستويات)."""
    flat = [lesson for level in LEVELS for lesson in level.lessons]
    for index, lesson in enumerate(flat):
        if lesson.key == lesson_key and index + 1 < len(flat):
            return flat[index + 1]
    return None


def first_lesson() -> Lesson:
    """أول درس في المنهج."""
    return LEVELS[0].lessons[0]


def all_lessons() -> tuple[Lesson, ...]:
    """كل الدروس بترتيبها."""
    return tuple(lesson for level in LEVELS for lesson in level.lessons)
