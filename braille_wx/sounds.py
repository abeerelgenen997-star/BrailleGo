"""أصوات التطبيق المميزة — مبنية على ``winsound`` في Windows.

تُشغّل النغمات في خيط منفصل حتى لا تتجمّد الواجهة. وإن تعذّر ``winsound``
يبقى التطبيق يعمل بصمت دون أي خطأ.

الأصوات كلها **داخل التطبيق** (تُولَّد نغميًا) فلا تحتاج أي ملفات خارجية:

* :meth:`SoundPlayer.welcome_tune` — موسيقى ترحيبية قصيرة عند أول تشغيل.
* :meth:`SoundPlayer.correct` — نغمة صاعدة مبهجة ومتنوّعة للإجابة الصحيحة.
* :meth:`SoundPlayer.incorrect` — نغمة هابطة لطيفة للإجابة الخاطئة.
* :meth:`SoundPlayer.encouragement` — عزف تشجيعي قصير بعد النجاح.
* :meth:`SoundPlayer.attention` — نغمة لافتة للانتباه (تناسب الطفل الكفيف).
* :meth:`SoundPlayer.celebrate` — نغمة احتفال عند إتمام مستوى أو جلسة.
* :meth:`SoundPlayer.click` — نقرة خفيفة عند تبديل نقطة أو التنقل.

نُوظّف التنويع وثبات الإيقاع اللذين يجذبان انتباه الطفل الكفيف ويعزّزان
إحساسه بالإنجاز، مع تجنّب أي نبرة قاسية عند الخطأ حتى لا تُحبط المتعلّم.
"""

from __future__ import annotations

import random
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
    def attention(self) -> None: ...
    def celebrate(self) -> None: ...
    def level_up(self) -> None: ...


class SoundPlayer:
    """مشغّل أصوات بسيط لأحداث التطبيق."""

    #: نغمات الإجابة الصحيحة: صاعدة ومبهجة ومتنوّعة (تُختار عشوائيًا).
    CORRECT_JINGLES: tuple[Sequence, ...] = (
        ((784, 90), (1047, 120)),
        ((880, 70), (1175, 70), (1568, 150)),
        ((1047, 70), (1319, 70), (1568, 170)),
    )
    #: توافق مع الاسم القديم.
    CORRECT: Sequence = CORRECT_JINGLES[0]
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
    #: عبارات تشجيع نغمية متنوّعة بعد الإجابة الصحيحة.
    ENCOURAGEMENTS: tuple[Sequence, ...] = (
        ((659, 90), (784, 90), (1047, 90), (1319, 200)),
        ((784, 70), (988, 70), (1175, 70), (1568, 220)),
        ((880, 60), (1109, 60), (1319, 60), (1760, 180)),
    )
    #: توافق مع الاسم القديم.
    ENCOURAGEMENT: Sequence = ENCOURAGEMENTS[0]
    #: نغمة لافتة للانتباه: نداءتان متساويتان ثم صعود واضح — تجذب انتباه
    #: الطفل الكفيف قبل المعلومة أو بعد الخطأ لتشجيعه على المحاولة.
    ATTENTION = ((1047, 80), (0, 45), (1047, 80), (1319, 160))
    #: احتفال عند إتمام مستوى أو جلسة كاملة.
    LEVEL_UP = (
        (523, 100), (659, 100), (784, 100), (1047, 100),
        (784, 100), (1047, 100), (1319, 300),
    )

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self._rng = random.Random()

    def _run(self, sequence: Sequence) -> None:
        if not self.enabled:
            return
        threading.Thread(target=_play, args=(sequence,), daemon=True).start()

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def correct(self) -> None:
        self._run(self._rng.choice(self.CORRECT_JINGLES))

    def incorrect(self) -> None:
        self._run(self.INCORRECT)

    def click(self) -> None:
        self._run(self.CLICK)

    def welcome_tune(self) -> None:
        self._run(self.WELCOME)

    def encouragement(self) -> None:
        self._run(self._rng.choice(self.ENCOURAGEMENTS))

    def attention(self) -> None:
        self._run(self.ATTENTION)

    def celebrate(self) -> None:
        self._run(self.LEVEL_UP)

    def level_up(self) -> None:
        self._run(self.LEVEL_UP)


__all__ = ["SoundPlayer", "NullSoundPlayer", "Sequence"]
