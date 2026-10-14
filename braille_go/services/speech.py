"""النطق (تحويل النص إلى كلام) — دعم اختياري بالكامل.

نستخدم ``QtTextToSpeech`` المدمج في PySide6 لأن ذلك يوفّر:

* عدم الحاجة إلى أي مكتبة إضافية (يبقى عدد الاعتماديات في أدنى حد).
* استخدام محرّك النطق المثبّت في نظام Windows (SAPI5) عبر Qt.
* ضبط السرعة ومستوى الصوت واختيار الصوت المتاح.

التطبيق **يعمل بدون صوت** إذا لم يتوفّر محرّك النطق أو لم يوجد صوت عربي مثبّت
على جهاز المستخدم؛ وفي هذه الحالة نُبلّغ المستخدم بوضوح بدل الفشل الصامت.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import QLocale, QObject, Signal

try:  # pragma: no cover - depends on the Qt build
    from PySide6.QtTextToSpeech import QTextToSpeech, QVoice

    _QT_TTS_AVAILABLE = True
except Exception:  # pragma: no cover
    QTextToSpeech = None  # type: ignore[assignment]
    QVoice = None  # type: ignore[assignment]
    _QT_TTS_AVAILABLE = False


@dataclass(frozen=True)
class VoiceInfo:
    """معلومات صوت متاح على الجهاز."""

    name: str
    locale: str
    language: str
    gender: str = ""


class NullSpeechService(QObject):
    """خدمة نطق صامتة تُستخدم عند غياب محرّك النطق.

    تحافظ على نفس الواجهة حتى لا تحتاج الواجهة الرسومية إلى أي شرط خاص.
    """

    spoken = Signal(str)
    state_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._last: str = ""
        self.available = False
        self.reason_ar = "محرّك النطق غير متوفّر في هذه النسخة من Qt."

    # -- configuration -------------------------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)

    def set_rate(self, rate: float) -> None:
        self._rate = rate

    def set_volume(self, volume: float) -> None:
        self._volume = volume

    def set_voice_name(self, name: str) -> None:
        self._voice_name = name

    def set_language(self, language: str) -> None:
        self._language = language

    # -- actions -------------------------------------------------------
    def say(self, text: str, language: str | None = None) -> None:
        self._last = text or ""

    def stop(self) -> None:
        pass

    def repeat(self) -> None:
        if self._last:
            self.say(self._last)

    def voices(self) -> list[VoiceInfo]:
        return []

    def has_language(self, language: str) -> bool:
        return False

    def status_text(self) -> str:
        return self.reason_ar

    @property
    def is_speaking(self) -> bool:
        return False

    @property
    def last_text(self) -> str:
        return self._last


class SpeechService(QObject):
    """خدمة نطق مبنية على ``QtTextToSpeech``."""

    spoken = Signal(str)
    state_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.available = False
        self.reason_ar = ""
        self._enabled = False
        self._rate = 0.0
        self._volume = 1.0
        self._voice_name = ""
        self._language = ""
        self._last = ""
        self._engine = None

        if not _QT_TTS_AVAILABLE:  # pragma: no cover - depends on Qt build
            self.reason_ar = "وحدة النطق غير متوفّرة في هذه النسخة من PySide6."
            return
        try:
            engines = QTextToSpeech.availableEngines()
        except Exception as exc:  # pragma: no cover
            self.reason_ar = f"تعذّر فحص محرّكات النطق: {exc}"
            return
        if not engines:
            self.reason_ar = "لا يوجد محرّك نطق مثبّت على هذا الجهاز."
            return
        try:
            self._engine = QTextToSpeech(self)
            self.available = True
        except Exception as exc:  # pragma: no cover
            self.reason_ar = f"تعذّر تشغيل محرّك النطق: {exc}"
            self._engine = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        if not enabled:
            self.stop()

    def set_rate(self, rate: float) -> None:
        self._rate = max(-1.0, min(1.0, float(rate)))
        if self._engine is not None:
            try:
                self._engine.setRate(self._rate)
            except Exception:  # pragma: no cover - engine specific
                pass

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, float(volume)))
        if self._engine is not None:
            try:
                self._engine.setVolume(self._volume)
            except Exception:  # pragma: no cover
                pass

    def set_voice_name(self, name: str) -> None:
        self._voice_name = name or ""
        if self._engine is None or not name:
            return
        for voice in self._engine.availableVoices():
            if voice.name() == name:
                try:
                    self._engine.setVoice(voice)
                except Exception:  # pragma: no cover
                    pass
                return

    def set_language(self, language: str) -> None:
        """اختيار اللغة المفضّلة للنطق (``"ar"`` أو ``"en"`` أو فراغ)."""
        self._language = language or ""
        if self._engine is None or not self._language:
            return
        locale = QLocale(QLocale.Arabic if self._language == "ar" else QLocale.English,
                         QLocale.AnyCountry)
        try:
            self._engine.setLocale(locale)
        except Exception:  # pragma: no cover - locale may be unsupported
            pass

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def voices(self) -> list[VoiceInfo]:
        if self._engine is None:
            return []
        result: list[VoiceInfo] = []
        try:
            for voice in self._engine.availableVoices():
                locale = voice.locale()
                result.append(
                    VoiceInfo(
                        name=voice.name(),
                        locale=locale.name(),
                        language=locale.name().split("_")[0].lower(),
                        gender=str(voice.gender()),
                    )
                )
        except Exception:  # pragma: no cover
            return result
        return result

    def has_language(self, language: str) -> bool:
        return any(v.language == language for v in self.voices())

    def status_text(self) -> str:
        if not self.available:
            return self.reason_ar or "النطق غير متاح."
        voices = self.voices()
        if not voices:
            return "محرّك النطق متاح لكن لا توجد أصوات مثبّتة."
        if not self.has_language("ar"):
            return (
                "لا يوجد صوت عربي مثبّت على الجهاز؛ سيبقى التطبيق قابلًا للاستخدام "
                "وقد يُنطق النص العربي بصوت مختلف أو لا يُنطق."
            )
        return f"النطق متاح ({len(voices)} صوت)."

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def say(self, text: str, language: str | None = None) -> None:
        """انطق النص إن كان النطق مُفعّلًا."""
        self._last = text or ""
        if self._engine is None or not self._enabled or not self._last:
            return
        if language:
            self.set_language(language)
        try:
            self._engine.stop()
            self._engine.say(self._last)
            self.spoken.emit(self._last)
        except Exception:  # pragma: no cover - never crash the UI for speech
            pass

    def stop(self) -> None:
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:  # pragma: no cover
                pass

    def repeat(self) -> None:
        if self._last:
            self.say(self._last)

    @property
    def is_speaking(self) -> bool:
        if self._engine is None:
            return False
        try:
            return self._engine.state() == QTextToSpeech.State.Speaking
        except Exception:  # pragma: no cover
            return False

    @property
    def last_text(self) -> str:
        return self._last


def create_speech_service(parent: QObject | None = None) -> SpeechService | NullSpeechService:
    """أنشئ خدمة النطق المناسبة بحسب ما هو متاح على الجهاز."""
    if not _QT_TTS_AVAILABLE:
        return NullSpeechService(parent)
    service = SpeechService(parent)
    if not service.available:
        return NullSpeechService(parent)
    return service


def qt_tts_available() -> bool:
    """هل وحدة النطق مضمّنة في نسخة PySide6 المستخدمة؟"""
    return _QT_TTS_AVAILABLE
