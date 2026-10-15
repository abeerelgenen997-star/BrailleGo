"""أصوات التطبيق المميزة — مبنية على ``winsound`` في Windows.

تُشغّل النغمات في خيط منفصل حتى لا تتجمّد الواجهة. وإن تعذّر ``winsound``
يبقى التطبيق يعمل بصمت دون أي خطأ.

الأصوات كلها **داخل التطبيق** (تُولَّد نغميًا) فلا تحتاج أي ملفات خارجية:

* :meth:`SoundPlayer.welcome_tune` — موسيقى ترحيبية قصيرة عند أول تشغيل.
* :meth:`SoundPlayer.correct` — نغمة صاعدة مبهجة للإجابة الصحيحة.
* :meth:`SoundPlayer.incorrect` — نغمة هابطة لطيفة للإجابة الخاطئة.
* :meth:`SoundPlayer.encouragement` — عزف قصير للتشجيع بعد نجاح.
* :meth:`SoundPlayer.level_up` — نغمة احتفال عند إتمام مستوى.
* :meth:`SoundPlayer.click` — نقرة خفيفة عند تبديل نقطة أو التنقل.
"""

from __future__ import annotations

import threading

try:  # pragma: no cover - platform dependent
    import winsound
except Exception:  # pragma: no cover
    winsound = None  # type: ignore[assignment]


#: المدد بالمللي ثانية، والترددات بالهرتز. القيمة 0 تعني سكتة قصيرة.
Sequence = tuple[tuple[int, int], ...]


def _play(sequence: Sequence) -> None:
    if winsound is None:
        return
    try:
        for freq, duration in sequence:
            if freq <= 0:
                # سكتة: نستخدم Beep بتردد مسموع مع خفض المدة لتفادي التقاط الصوت.
                winsound.Beep(37, int(duration))  # 37 هرتز = شبه صامت
            else:
                winsound.Beep(int(freq), int(duration))
    except Exception:  # pragma: no cover - never crash for sound
        pass


class NullSoundPlayer:
    """مشغّل صامت يُستخدم عند تعطيل الأصوات أو غياب ``winsound``."""

    enabled = False

    def correct(self) -> None: ...
    def incorrect(self) -> None: ...
    def click(self) -> None: ...
    def welcome_tune(self) -> None: ...
    def encouragement(self) -> None: ...
    def level_up(self) -> None: ...


class SoundPlayer:
    """مشغّل أصوات بسيط لأحداث التطبيق."""

    #: نغمة الإجابة الصحيحة: صاعدة ومبهجة.
    CORRECT = ((784, 90), (1047, 120))
    #: نغمة الإجابة الخاطئة: هابطة لطيفة (غير قاسية حتى لا تُحبط المتعلّم).
    INCORRECT = ((440, 110), (330, 150))
    #: نقرة خفيفة لتبديل نقطة أو التنقل.
    CLICK = ((1200, 40),)
    #: لحن ترحيبي قصير ودافئ يُعزف عند أول تشغيل (داخل التطبيق).
    WELCOME = (
        (523, 140), (659, 140), (784, 140), (1047, 260),
        (0, 60),
        (784, 140), (880, 140), (1047, 320),
    )
    #: عبارة تشجيع نغمية بعد الإجابة الصحيحة.
    ENCOURAGEMENT = ((659, 90), (784, 90), (1047, 90), (1319, 200))
    #: احتفال عند إتمام مستوى.
    LEVEL_UP = (
        (523, 100), (659, 100), (784, 100), (1047, 100),
        (784, 100), (1047, 100), (1319, 300),
    )

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = bool(enabled)

    def _run(self, sequence: Sequence) -> None:
        if not self.enabled:
            return
        threading.Thread(target=_play, args=(sequence,), daemon=True).start()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def correct(self) -> None:
        self._run(self.CORRECT)

    def incorrect(self) -> None:
        self._run(self.INCORRECT)

    def click(self) -> None:
        self._run(self.CLICK)

    def welcome_tune(self) -> None:
        self._run(self.WELCOME)

    def encouragement(self) -> None:
        self._run(self.ENCOURAGEMENT)

    def level_up(self) -> None:
        self._run(self.LEVEL_UP)


__all__ = ["SoundPlayer", "NullSoundPlayer", "Sequence"]
