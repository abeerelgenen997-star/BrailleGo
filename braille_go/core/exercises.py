"""محرك التدريبات: توليد الأسئلة وتصحيح الإجابات.

The engine is intentionally free of any GUI dependency so it can be unit
tested directly.  A :class:`Exercise` is a complete, self-contained question:
the generator decides what to show, what the expected answer is and how that
answer is expressed, and the grader compares a learner response against it and
produces a human readable Arabic explanation.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, Sequence

from . import braille_text as bt
from . import i18n as _i18n
from .braille import BrailleCell, differing_dots
from .curriculum import Lesson, _SIMILAR_PAIRS  # noqa: F401  (pairs reused by review)
from .exercise_types import AnswerMode, ExerciseKind
from .symbols import BrailleSymbol, SymbolCategory, SymbolRepository, build_default_repository


@dataclass
class Exercise:
    """سؤال واحد كامل مع بيانات تصحيحه."""

    key: str
    kind: ExerciseKind
    lesson_key: str
    prompt_ar: str
    answer_mode: AnswerMode
    language: str = "ar"
    stimulus_text: str = ""
    stimulus_braille: str = ""
    options: tuple[str, ...] = ()
    option_patterns: tuple[tuple[BrailleCell, ...], ...] = ()
    option_labels: tuple[str, ...] = ()
    correct_answer: str = ""
    correct_dots: tuple[int, ...] = ()
    correct_cells: tuple[tuple[int, ...], ...] = ()
    symbol_keys: tuple[str, ...] = ()
    explanation_ar: str = ""
    hint_ar: str = ""
    show_target_text: bool = False
    letter_count: int = 1

    # ------------------------------------------------------------------
    @property
    def is_multicell_build(self) -> bool:
        return self.answer_mode == AnswerMode.BUILD_CELLS

    def speak_prompt(self) -> str:
        """نص جاهز للنطق عند طلب المساعدة الصوتية."""
        parts = [self.prompt_ar]
        if self.show_target_text and self.stimulus_text:
            parts.append(self.stimulus_text)
        return " ".join(part for part in parts if part)


@dataclass
class Feedback:
    """نتيجة تصحيح إجابة."""

    correct: bool
    message_ar: str
    title_ar: str
    explanation_ar: str = ""
    expected: str = ""
    given: str = ""

    @property
    def spoken(self) -> str:
        return " ".join(p for p in (self.title_ar, self.message_ar, self.explanation_ar) if p)


def _normalise_text(value: str, language: str = "ar") -> str:
    """تطبيع بسيط للنصوص لمقارنة الإجابات المكتوبة."""
    text = (value or "").strip()
    # إزالة التشكيل عند المقارنة لتفادي إرباك المتعلّم.
    if language == "ar":
        text = "".join(ch for ch in text if not ("\u064b" <= ch <= "\u0652"))
    return text


# ----------------------------------------------------------------------
# أدوات النصوص متعدّدة اللغات (الأسئلة والتغذية الراجعة)
# ----------------------------------------------------------------------
def _t(key: str, **kwargs) -> str:
    """نصّ مترجم من نظام الترجمة الأساسي (يتبع لغة الواجهة الحالية)."""
    return _i18n.t(key, **kwargs)


def _sep() -> str:
    """الفاصل بين العناصر (فاصلة عربية أو لاتينية حسب اللغة)."""
    return _i18n.t("ex_separator")


def _dots_label(dots: Sequence[int]) -> str:
    """تمثيل نصّي لنقاط برايل بفاصل مناسب للغة."""
    ordered = sorted(int(d) for d in dots)
    return _sep().join(str(d) for d in ordered) or _t("ex_blank")


def _symbol_name(symbol: BrailleSymbol) -> str:
    """اسم الرمز بلغة الواجهة إن توفّر، وإلا فالعربية."""
    if _i18n.get_lang() != "ar" and symbol.name_en:
        return symbol.name_en
    return symbol.name_ar


def _symbol_dots(symbol: BrailleSymbol) -> str:
    return symbol.dots_text() or _t("ex_blank")


def _difference(a: BrailleCell, b: BrailleCell) -> str:
    """اشرح بلغة الواجهة الفرق بين الخلية ``a`` والمتوقّعة ``b``."""
    missing, extra = differing_dots(a, b)
    parts: list[str] = []
    if missing:
        parts.append(_t("ex_diff_missing", dots=_sep().join(str(d) for d in missing)))
    if extra:
        parts.append(_t("ex_diff_extra", dots=_sep().join(str(d) for d in extra)))
    if not parts:
        return _t("ex_diff_same")
    return _sep().join(parts)


def _dot_distance(a: BrailleSymbol, b: BrailleSymbol) -> int:
    return len(set(a.dots) ^ set(b.dots))


def _pool_for(symbol: BrailleSymbol, repo: SymbolRepository) -> list[BrailleSymbol]:
    """أعد مجموعة الرموز المناسبة لاختيار مشتّتات منها."""
    if symbol.category is SymbolCategory.LETTER_EN:
        return [s for s in repo.by_category(SymbolCategory.LETTER_EN)]
    if symbol.category is SymbolCategory.LETTER_AR:
        return [s for s in repo.by_category(SymbolCategory.LETTER_AR)]
    if symbol.category is SymbolCategory.DIGIT:
        return [s for s in repo.by_category(SymbolCategory.DIGIT)]
    if symbol.category is SymbolCategory.DIACRITIC:
        return [s for s in repo.by_category(SymbolCategory.DIACRITIC)]
    if symbol.category is SymbolCategory.PUNCTUATION:
        candidates = repo.by_category(SymbolCategory.PUNCTUATION)
        same = [s for s in candidates if s.language == symbol.language]
        return same or list(candidates)
    if symbol.category is SymbolCategory.SYMBOL:
        return list(repo.by_category(SymbolCategory.SYMBOL))
    return [s for s in repo.all() if s.category is symbol.category]


def _choose_distractors(
    symbol: BrailleSymbol,
    repo: SymbolRepository,
    rng: random.Random,
    count: int,
    must_include: Iterable[str] = (),
) -> list[BrailleSymbol]:
    """اختر مشتّتات، مع تفضيل الرموز المتشابهة في النقاط."""
    pool = [s for s in _pool_for(symbol, repo) if s.key != symbol.key and s.char != symbol.char]
    required = [repo.require(k) for k in must_include if k in repo and k != symbol.key]

    chosen: list[BrailleSymbol] = []
    for item in required:
        if item.key not in {c.key for c in chosen} and item.char != symbol.char:
            chosen.append(item)

    pool = [s for s in pool if s.key not in {c.key for c in chosen}]
    # رتّب حسب التشابه مع الرمز الهدف، ثم اختر من الأقرب مع شيء من العشوائية.
    pool.sort(key=lambda s: _dot_distance(s, symbol))
    close = pool[: max(count * 3, count)]
    rng.shuffle(close)
    for candidate in close:
        if len(chosen) >= count:
            break
        if candidate.char not in {c.char for c in chosen}:
            chosen.append(candidate)

    # في حال نقص العدد، أكمل من بقية المجموعة.
    if len(chosen) < count:
        rest = [s for s in pool if s.key not in {c.key for c in chosen}]
        rng.shuffle(rest)
        for candidate in rest:
            if len(chosen) >= count:
                break
            if candidate.char not in {c.char for c in chosen}:
                chosen.append(candidate)
    return chosen[:count]


class ExerciseGenerator:
    """مولّد التدريبات لدروس المنهج."""

    def __init__(
        self,
        repository: SymbolRepository | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.repo = repository or build_default_repository()
        self.rng = rng or random.Random()

    # ------------------------------------------------------------------
    def generate_lesson(self, lesson: Lesson, count: int | None = None) -> list[Exercise]:
        """ولّد قائمة تدريبات لدرس كامل."""
        total = count or lesson.exercise_count
        if not lesson.exercise_kinds:
            return []
        symbols = self.repo.many(lesson.symbol_keys)
        exercises: list[Exercise] = []
        attempts = 0
        max_attempts = total * 6
        while len(exercises) < total and attempts < max_attempts:
            attempts += 1
            kind = self.rng.choice(list(lesson.exercise_kinds))
            exercise = self._generate_one(lesson, kind, len(exercises), symbols)
            if exercise is None:
                continue
            if exercise.key in {e.key for e in exercises}:
                continue
            exercises.append(exercise)
        return exercises

    def generate_review(self, lesson_key: str, symbol_keys: Sequence[str], count: int = 8) -> list[Exercise]:
        """ولّد تدريبات مراجعة مركّزة على رموز محددة (الأخطاء السابقة)."""
        symbols = self.repo.many(symbol_keys)
        if not symbols:
            return []
        lesson = Lesson(
            key=lesson_key,
            title_ar=_t("ex_review_title"),
            description_ar=_t("ex_review_desc"),
            symbol_keys=tuple(s.key for s in symbols),
            exercise_kinds=(
                ExerciseKind.IDENTIFY_CHAR,
                ExerciseKind.BUILD_PATTERN,
                ExerciseKind.DISCRIMINATE,
            ),
            exercise_count=count,
        )
        return self.generate_lesson(lesson, count=count)

    # ------------------------------------------------------------------
    def _generate_one(
        self,
        lesson: Lesson,
        kind: ExerciseKind,
        index: int,
        symbols: Sequence[BrailleSymbol],
    ) -> Exercise | None:
        try:
            if kind is ExerciseKind.BUILD_FROM_DESCRIPTION:
                return self._build_from_description(lesson, index)
            if kind is ExerciseKind.IDENTIFY_CHAR and symbols:
                return self._identify_char(lesson, index, symbols)
            if kind is ExerciseKind.IDENTIFY_PATTERN and symbols:
                return self._identify_pattern(lesson, index, symbols)
            if kind is ExerciseKind.BUILD_PATTERN and symbols:
                return self._build_pattern(lesson, index, symbols)
            if kind is ExerciseKind.TYPE_ANSWER and symbols:
                return self._type_answer(lesson, index, symbols)
            if kind is ExerciseKind.DISCRIMINATE and symbols:
                return self._discriminate(lesson, index, symbols)
            if kind is ExerciseKind.NUMBER_EXERCISE:
                return self._number_exercise(lesson, index)
            if kind is ExerciseKind.PUNCTUATION_EXERCISE and symbols:
                return self._punctuation_exercise(lesson, index, symbols)
            if kind is ExerciseKind.BUILD_WORD:
                return self._word_exercise(lesson, index, build=True)
            if kind is ExerciseKind.READ_WORD:
                return self._word_exercise(lesson, index, build=False)
            if kind is ExerciseKind.READ_SENTENCE:
                return self._sentence_exercise(lesson, index)
            if kind is ExerciseKind.MATCH_LETTER and symbols:
                return self._match_letter(lesson, index, symbols)
        except (KeyError, ValueError, IndexError):
            return None
        return None

    def generate_matching(self, count: int = 8, language: str = "ar") -> list[Exercise]:
        """ولّد تدريبات تطابق الحرف المطبوع مع نمط برايل.

        تُستخدم خصوصًا للمتعلّم المبصر ليربط بين شكل الحرف المطبوع ونمط
        برايل الخاص به.
        """
        category = SymbolCategory.LETTER_EN if language == "en" else SymbolCategory.LETTER_AR
        letters = self.repo.by_category(category)
        if not letters:
            return []
        lesson = Lesson(
            key=f"matching_{language}",
            title_ar=_t("ex_match_lesson_title"),
            description_ar=_t("ex_match_lesson_desc"),
            symbol_keys=tuple(s.key for s in letters),
            exercise_kinds=(ExerciseKind.MATCH_LETTER,),
            language=language,
            exercise_count=count,
        )
        return self.generate_lesson(lesson, count=count)

    # ------------------------------------------------------------------
    # Generators
    # ------------------------------------------------------------------
    def _build_from_description(self, lesson: Lesson, index: int) -> Exercise:
        size = self.rng.randint(1, 4)
        dots = sorted(self.rng.sample(range(1, 7), size))
        dots_text = _dots_label(dots)
        return Exercise(
            key=f"{lesson.key}:build_desc:{index}:{'-'.join(map(str, dots))}",
            kind=ExerciseKind.BUILD_FROM_DESCRIPTION,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_build_desc", dots=dots_text),
            answer_mode=AnswerMode.BUILD_CELL,
            correct_answer="-".join(map(str, dots)),
            correct_dots=tuple(dots),
            explanation_ar=_t("ex_explain_build_desc", dots=dots_text),
            hint_ar="استخدم مفاتيح الأرقام 1 إلى 6 لتبديل النقاط.",
        )

    def _identify_char(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        symbol = self.rng.choice(list(symbols))
        distractors = _choose_distractors(symbol, self.repo, self.rng, 3)
        options = [symbol.char, *(d.char for d in distractors)]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:ident:{index}:{symbol.key}",
            kind=ExerciseKind.IDENTIFY_CHAR,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_identify"),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language=symbol.language,
            stimulus_braille=symbol.full_unicode(),
            options=tuple(options),
            correct_answer=symbol.char,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_identify",
                pattern=symbol.full_unicode(),
                char=symbol.char,
                name=_symbol_name(symbol),
                dots=_symbol_dots(symbol),
            ),
            hint_ar="تذكّر ترتيب النقاط: 1 و4 في الأعلى، 2 و5 في الوسط، 3 و6 في الأسفل.",
        )

    def _identify_pattern(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        symbol = self.rng.choice(list(symbols))
        distractors = _choose_distractors(symbol, self.repo, self.rng, 3)
        candidates = [symbol, *distractors]
        self.rng.shuffle(candidates)
        option_patterns = tuple((s.cell,) for s in candidates)
        option_labels = tuple(_symbol_dots(s) for s in candidates)
        return Exercise(
            key=f"{lesson.key}:pattern:{index}:{symbol.key}",
            kind=ExerciseKind.IDENTIFY_PATTERN,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_choose_pattern", char=symbol.char),
            answer_mode=AnswerMode.CHOOSE_PATTERN,
            language=symbol.language,
            stimulus_text=symbol.char,
            show_target_text=True,
            options=option_labels,
            option_patterns=option_patterns,
            option_labels=option_labels,
            correct_answer=_symbol_dots(symbol),
            correct_dots=symbol.dots,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_choose_pattern",
                char=symbol.char,
                dots=_symbol_dots(symbol),
                pattern=symbol.full_unicode(),
            ),
        )

    def _build_pattern(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        symbol = self.rng.choice(list(symbols))
        return Exercise(
            key=f"{lesson.key}:build:{index}:{symbol.key}",
            kind=ExerciseKind.BUILD_PATTERN,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_build_pattern", char=symbol.char),
            answer_mode=AnswerMode.BUILD_CELL,
            language=symbol.language,
            stimulus_text=symbol.char,
            show_target_text=True,
            correct_answer=_symbol_dots(symbol),
            correct_dots=symbol.dots,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_build_pattern",
                char=symbol.char,
                name=_symbol_name(symbol),
                dots=_symbol_dots(symbol),
            ),
            hint_ar="حدّد النقاط واحدة واحدة، ثم اضغط «تأكيد الإجابة».",
        )

    def _type_answer(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        symbol = self.rng.choice(list(symbols))
        return Exercise(
            key=f"{lesson.key}:type:{index}:{symbol.key}",
            kind=ExerciseKind.TYPE_ANSWER,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_type"),
            answer_mode=AnswerMode.TYPE_TEXT,
            language=symbol.language,
            stimulus_braille=symbol.full_unicode(),
            correct_answer=symbol.char,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_type",
                pattern=symbol.full_unicode(),
                char=symbol.char,
                name=_symbol_name(symbol),
            ),
            hint_ar="يمكنك أيضًا استخدام الخلية التفاعلية لتكوين النمط والتحقق من نفسك.",
        )

    def _discriminate(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        pairs = lesson.discrimination_pairs or _SIMILAR_PAIRS
        pair = self.rng.choice(list(pairs))
        if pair[0] not in self.repo or pair[1] not in self.repo:
            pair = _SIMILAR_PAIRS[0]
        target = self.repo.require(self.rng.choice(pair))
        confusable = self.repo.require(pair[0] if target.key == pair[1] else pair[1])
        distractors = _choose_distractors(
            target, self.repo, self.rng, 2, must_include=(confusable.key,)
        )
        options = [target.char, confusable.char, *(d.char for d in distractors)]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:disc:{index}:{target.key}:{confusable.key}",
            kind=ExerciseKind.DISCRIMINATE,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_discriminate"),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language=target.language,
            stimulus_braille=target.full_unicode(),
            options=tuple(options),
            correct_answer=target.char,
            symbol_keys=(target.key, confusable.key),
            explanation_ar=_t(
                "ex_explain_discriminate",
                pattern=target.full_unicode(),
                char=target.char,
                dots=target.dots_text(),
                other=confusable.char,
                otherdots=confusable.dots_text(),
                otherpattern=confusable.full_unicode(),
            ),
            hint_ar="ركّز على النقاط التي تختلف فيها الخليتان فقط.",
        )

    def _number_exercise(self, lesson: Lesson, index: int) -> Exercise:
        digits = self.repo.by_category(SymbolCategory.DIGIT)
        if not digits:
            raise ValueError("لا توجد أرقام في البيانات")
        symbol = self.rng.choice(digits)
        others = [d for d in digits if d.key != symbol.key]
        self.rng.shuffle(others)
        options = [symbol.char, *(d.char for d in others[:3])]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:num:{index}:{symbol.key}",
            kind=ExerciseKind.NUMBER_EXERCISE,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_number"),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language="ar",
            stimulus_braille=symbol.full_unicode(),
            options=tuple(options),
            correct_answer=symbol.char,
            symbol_keys=(symbol.key, "sym_number_sign"),
            explanation_ar=_t(
                "ex_explain_number",
                dots=symbol.dots_text(),
                char=symbol.char,
                pattern=symbol.full_unicode(),
            ),
            hint_ar="اقرأ أولًا ⠼ (النقاط 3-4-5-6) ثم اقرأ الخلية التالية.",
        )

    def _punctuation_exercise(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        punctuations = [s for s in symbols if s.category is SymbolCategory.PUNCTUATION] or list(symbols)
        symbol = self.rng.choice(punctuations)
        others = [s for s in self.repo.by_category(SymbolCategory.PUNCTUATION) if s.key != symbol.key]
        self.rng.shuffle(others)
        options = [symbol.char, *(o.char for o in others[:3])]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:punct:{index}:{symbol.key}",
            kind=ExerciseKind.PUNCTUATION_EXERCISE,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_punct", pattern=symbol.full_unicode()),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language=symbol.language,
            stimulus_braille=symbol.full_unicode(),
            options=tuple(options),
            correct_answer=symbol.char,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_punct",
                char=symbol.char,
                name=_symbol_name(symbol),
                dots=symbol.dots_text(),
                notes=symbol.notes_ar if _i18n.get_lang() == "ar" else "",
            ).strip(),
            hint_ar="تذكّر أن أنظمة الترقيم تختلف بين العربية والإنجليزية.",
        )

    def _word_exercise(self, lesson: Lesson, index: int, build: bool) -> Exercise:
        words = list(lesson.words) or (_ARABIC_WORDS_FALLBACK if lesson.language == "ar" else _ENGLISH_WORDS_FALLBACK)
        word = self.rng.choice(words)
        transcription = bt.transcribe(word, lesson.language)
        if build:
            return Exercise(
                key=f"{lesson.key}:buildword:{index}:{word}",
                kind=ExerciseKind.BUILD_WORD,
                lesson_key=lesson.key,
                prompt_ar=_t("ex_prompt_build_word", word=word),
                answer_mode=AnswerMode.BUILD_CELLS,
                language=lesson.language,
                stimulus_text=word,
                show_target_text=True,
                correct_answer=word,
                correct_cells=transcription.dots,
                letter_count=len(transcription.cells),
                explanation_ar=_t(
                    "ex_explain_build_word", word=word, pattern=transcription.unicode
                ),
                hint_ar="املأ خلية لكل حرف بالترتيب من اليسار إلى اليمين.",
            )
        others = [w for w in words if w != word]
        self.rng.shuffle(others)
        options = [word, *others[:3]]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:readword:{index}:{word}",
            kind=ExerciseKind.READ_WORD,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_read_word"),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language=lesson.language,
            stimulus_braille=transcription.unicode,
            options=tuple(options),
            correct_answer=word,
            explanation_ar=_t(
                "ex_explain_read_word", pattern=transcription.unicode, word=word
            ),
            hint_ar="اقرأ الخلايا واحدة تلو الأخرى ثم اجمع الحروف.",
        )

    def _match_letter(self, lesson: Lesson, index: int, symbols: Sequence[BrailleSymbol]) -> Exercise:
        letters = [
            s for s in symbols
            if s.category in (SymbolCategory.LETTER_AR, SymbolCategory.LETTER_EN)
        ] or list(symbols)
        symbol = self.rng.choice(letters)
        distractors = _choose_distractors(symbol, self.repo, self.rng, 3)
        candidates = [symbol, *distractors]
        self.rng.shuffle(candidates)
        option_patterns = tuple((s.cell,) for s in candidates)
        option_labels = tuple(_symbol_dots(s) for s in candidates)
        return Exercise(
            key=f"{lesson.key}:match:{index}:{symbol.key}",
            kind=ExerciseKind.MATCH_LETTER,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_match", char=symbol.char),
            answer_mode=AnswerMode.CHOOSE_PATTERN,
            language=symbol.language,
            stimulus_text=symbol.char,
            show_target_text=True,
            options=option_labels,
            option_patterns=option_patterns,
            option_labels=option_labels,
            correct_answer=_symbol_dots(symbol),
            correct_dots=symbol.dots,
            symbol_keys=(symbol.key,),
            explanation_ar=_t(
                "ex_explain_match",
                char=symbol.char,
                name=_symbol_name(symbol),
                dots=_symbol_dots(symbol),
                pattern=symbol.full_unicode(),
            ),
            hint_ar="قارن النقاط في كل خيار واختر النمط المطابق للحرف.",
        )

    def _sentence_exercise(self, lesson: Lesson, index: int) -> Exercise:
        sentences = list(lesson.sentences) or (
            _ARABIC_SENTENCES_FALLBACK if lesson.language == "ar" else _ENGLISH_SENTENCES_FALLBACK
        )
        sentence = self.rng.choice(sentences)
        transcription = bt.transcribe(sentence, lesson.language)
        others = [s for s in sentences if s != sentence]
        self.rng.shuffle(others)
        options = [sentence, *others[:3]]
        self.rng.shuffle(options)
        return Exercise(
            key=f"{lesson.key}:sentence:{index}:{sentence}",
            kind=ExerciseKind.READ_SENTENCE,
            lesson_key=lesson.key,
            prompt_ar=_t("ex_prompt_read_sentence"),
            answer_mode=AnswerMode.CHOOSE_TEXT,
            language=lesson.language,
            stimulus_braille=transcription.unicode,
            options=tuple(options),
            correct_answer=sentence,
            explanation_ar=_t(
                "ex_explain_read_sentence",
                pattern=transcription.unicode,
                sentence=sentence,
            ),
            hint_ar="الفراغ في برايل يفصل بين الكلمات كما في الكتابة العادية.",
        )


_ARABIC_WORDS_FALLBACK = (
    "باب", "بيت", "نور", "علم", "قلم", "شمس", "قمر",
    "كتاب", "سلام", "ولد", "درس", "ماء",
)
_ENGLISH_WORDS_FALLBACK = (
    "cat", "dog", "sun", "moon", "book", "pen", "hat",
    "bus", "red", "big", "man", "map",
)
_ARABIC_SENTENCES_FALLBACK = (
    "السلام عليكم", "هذا كتاب", "البيت كبير", "أنا أتعلم برايل", "القلم على المكتب",
)
_ENGLISH_SENTENCES_FALLBACK = ("I can read", "The sun is hot", "This is a book", "We learn braille")


# ----------------------------------------------------------------------
# Grading
# ----------------------------------------------------------------------
def grade(exercise: Exercise, response: object, repository: SymbolRepository | None = None) -> Feedback:
    """صحّح إجابة المتعلّم مقابل التمرين.

    ``response`` can be a string, a :class:`BrailleCell`, an iterable of dots or
    a sequence of cells, depending on ``exercise.answer_mode``.
    """
    mode = exercise.answer_mode

    if mode is AnswerMode.CHOOSE_TEXT:
        given = str(response or "").strip()
        correct = given == exercise.correct_answer or (
            exercise.language == "en"
            and given.casefold() == exercise.correct_answer.casefold()
        )
        return _feedback_from_bool(exercise, correct, given, exercise.correct_answer)

    if mode is AnswerMode.TYPE_TEXT:
        given_raw = str(response or "")
        given = _normalise_text(given_raw, exercise.language)
        expected = _normalise_text(exercise.correct_answer, exercise.language)
        correct = bool(given) and (
            given == expected
            or (exercise.language == "en" and given.casefold() == expected.casefold())
        )
        if not given:
            return Feedback(
                correct=False,
                title_ar=_t("ex_fb_no_input_title"),
                message_ar=_t("ex_fb_no_input_msg"),
                explanation_ar=exercise.explanation_ar,
                expected=exercise.correct_answer,
                given="",
            )
        return _feedback_from_bool(exercise, correct, given_raw.strip(), exercise.correct_answer)

    if mode is AnswerMode.CHOOSE_PATTERN:
        index = response
        if isinstance(index, str):
            try:
                index = exercise.option_labels.index(index)
            except ValueError:
                index = -1
        try:
            index = int(index)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            index = -1
        if index < 0 or index >= len(exercise.option_patterns):
            return Feedback(
                correct=False,
                title_ar=_t("ex_fb_no_pattern_title"),
                message_ar=_t("ex_fb_no_pattern_msg"),
                explanation_ar=exercise.explanation_ar,
                expected=exercise.correct_answer,
                given="",
            )
        chosen = exercise.option_patterns[index]
        dots = chosen[0].dots if chosen else ()
        correct = tuple(dots) == tuple(exercise.correct_dots)
        given_label = exercise.option_labels[index] if index < len(exercise.option_labels) else str(dots)
        return _feedback_from_bool(exercise, correct, given_label, exercise.correct_answer)

    if mode is AnswerMode.BUILD_CELL:
        given_dots = _coerce_dots(response)
        correct = given_dots == tuple(sorted(exercise.correct_dots))
        diff = ""
        if not correct:
            diff = _difference(
                BrailleCell.from_dots(given_dots),
                BrailleCell.from_dots(exercise.correct_dots),
            )
        return _feedback_from_bool(
            exercise, correct, "-".join(map(str, given_dots)) or _t("ex_blank"),
            "-".join(map(str, exercise.correct_dots)) or _t("ex_blank"), detail=diff,
        )

    if mode is AnswerMode.BUILD_CELLS:
        given_cells = _coerce_cells(response)
        expected_cells = tuple(tuple(sorted(c)) for c in exercise.correct_cells)
        correct = tuple(sorted(c) for c in given_cells) == expected_cells
        if not correct:
            if len(given_cells) != len(expected_cells):
                detail = _t(
                    "ex_fb_cells_count",
                    given=len(given_cells),
                    expected=len(expected_cells),
                )
            else:
                details = []
                for position, (given, want) in enumerate(zip(given_cells, expected_cells), start=1):
                    if tuple(sorted(given)) != tuple(sorted(want)):
                        details.append(
                            _t(
                                "ex_fb_cell_pos",
                                n=position,
                                detail=_difference(
                                    BrailleCell.from_dots(given),
                                    BrailleCell.from_dots(want),
                                ),
                            )
                        )
                detail = _sep().join(details)
            return _feedback_from_bool(
                exercise, False, _cells_plain(given_cells), _cells_plain(expected_cells), detail=detail,
            )
        return _feedback_from_bool(
            exercise, True, _cells_plain(given_cells), _cells_plain(expected_cells),
        )

    return Feedback(
        correct=False,
        title_ar=_t("ex_fb_unsupported_title"),
        message_ar=_t("ex_fb_unsupported_msg"),
        explanation_ar=exercise.explanation_ar,
    )


def _coerce_dots(response: object) -> tuple[int, ...]:
    if isinstance(response, BrailleCell):
        return response.dots
    if response is None:
        return ()
    if isinstance(response, (set, frozenset, list, tuple)):
        try:
            return tuple(sorted(int(d) for d in response))
        except (TypeError, ValueError):
            return ()
    if isinstance(response, str):
        return BrailleCell.from_dot_string(response).dots
    if isinstance(response, int):
        return BrailleCell.from_bitmask(response).dots
    return ()


def _coerce_cells(response: object) -> tuple[tuple[int, ...], ...]:
    if response is None:
        return ()
    if isinstance(response, (list, tuple)):
        cells = []
        for item in response:
            cells.append(_coerce_dots(item))
        return tuple(cells)
    return ()


def _cells_plain(cells: Sequence[tuple[int, ...]]) -> str:
    parts = ["-".join(str(d) for d in cell) or _t("ex_blank") for cell in cells]
    return " | ".join(parts)


def _feedback_from_bool(
    exercise: Exercise,
    correct: bool,
    given: str,
    expected: str,
    detail: str = "",
) -> Feedback:
    if correct:
        return Feedback(
            correct=True,
            title_ar=_t("ex_fb_correct_title"),
            message_ar=_t("ex_fb_correct_msg"),
            explanation_ar=exercise.explanation_ar,
            expected=expected,
            given=given,
        )
    message = _t("ex_fb_wrong_msg")
    if detail:
        message += " " + detail
    return Feedback(
        correct=False,
        title_ar=_t("ex_fb_wrong_title"),
        message_ar=message + _t("ex_fb_try_again"),
        explanation_ar=exercise.explanation_ar,
        expected=expected,
        given=given,
    )


def similar_pairs() -> tuple[tuple[str, str], ...]:
    """أزواج الرموز المتشابهة المشتركة (تُستخدم في توليد المراجعة)."""
    return _SIMILAR_PAIRS
