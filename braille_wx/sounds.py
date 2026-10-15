"""أصوات التطبيق المميزة (صحيح/خطأ) — مبنية على ``winsound`` في Windows.

تُشغّل النغمات في خيط منفصل حتى لا تتجمّد الواجهة. وإن تعذّر ``winsound``
يبقى التطبيق يعمل بصمت دون أي خطأ.
"""

from __future__ import annotations

import threading

try:  # pragma: no cover - platform dependent
    import winsound
except Exception:  # pragma: no cover
    winsound = None  # type: ignore[assignment]


def _play(sequence: tuple[tuple[int, int], ...]) -> None:
    if winsound is None:
        return
    try:
        for freq, duration in sequence:
            winsound.Beep(int(freq), int(duration))
    except Exception:  # pragma: no cover - never crash for sound
        pass


class SoundPlayer:
    """مشغّل أصوات بسيط لأحداث التطبيق."""

    #: نغمة الإجابة الصحيحة: صاعدة ومبهجة.
    CORRECT = ((784, 90), (1047, 120))
    #: نغمة الإجابة الخاطئة: هابطة.
    INCORRECT = ((392, 130), (262, 170))
    #: نقرة خفيفة لتبديل نقطة أو التنقل.
    CLICK = ((1200, 40),)

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = bool(enabled)

    def _run(self, sequence: tuple[tuple[int, int], ...]) -> None:
        if not self.enabled:
            return
        threading.Thread(target=_play, args=(sequence,), daemon=True).start()

    def correct(self) -> None:
        self._run(self.CORRECT)

    def incorrect(self) -> None:
        self._run(self.INCORRECT)

    def click(self) -> None:
        self._run(self.CLICK)
