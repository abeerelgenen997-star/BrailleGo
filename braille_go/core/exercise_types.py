"""أنواع التدريبات وأساليب الإجابة.

Kept in its own module so that :mod:`braille_go.core.curriculum` and
:mod:`braille_go.core.exercises` can both depend on it without creating an
import cycle.
"""

from __future__ import annotations

from enum import Enum


class ExerciseKind(str, Enum):
    """أنواع التدريبات المدعومة."""

    INTRO = "intro"
    BUILD_FROM_DESCRIPTION = "build_from_description"
    IDENTIFY_CHAR = "identify_char"
    IDENTIFY_PATTERN = "identify_pattern"
    BUILD_PATTERN = "build_pattern"
    TYPE_ANSWER = "type_answer"
    DISCRIMINATE = "discriminate"
    NUMBER_EXERCISE = "number"
    PUNCTUATION_EXERCISE = "punctuation"
    BUILD_WORD = "build_word"
    READ_WORD = "read_word"
    READ_SENTENCE = "read_sentence"

    @property
    def label_ar(self) -> str:
        return _KIND_LABELS[self]


_KIND_LABELS: dict[ExerciseKind, str] = {
    ExerciseKind.INTRO: "تعريفي",
    ExerciseKind.BUILD_FROM_DESCRIPTION: "تكوين خلية",
    ExerciseKind.IDENTIFY_CHAR: "تعرّف على الرمز",
    ExerciseKind.IDENTIFY_PATTERN: "اختر نمط برايل",
    ExerciseKind.BUILD_PATTERN: "كوّن نمط برايل",
    ExerciseKind.TYPE_ANSWER: "اكتب الإجابة",
    ExerciseKind.DISCRIMINATE: "تمييز الرموز المتشابهة",
    ExerciseKind.NUMBER_EXERCISE: "تدريب على الأرقام",
    ExerciseKind.PUNCTUATION_EXERCISE: "تدريب على الترقيم",
    ExerciseKind.BUILD_WORD: "تكوين كلمة",
    ExerciseKind.READ_WORD: "قراءة كلمة",
    ExerciseKind.READ_SENTENCE: "قراءة جملة",
}


class AnswerMode(str, Enum):
    """طريقة إدخال الإجابة."""

    CHOOSE_TEXT = "choose_text"
    CHOOSE_PATTERN = "choose_pattern"
    BUILD_CELL = "build_cell"
    BUILD_CELLS = "build_cells"
    TYPE_TEXT = "type_text"
