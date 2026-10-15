"""خدمة النطق (تحويل النص إلى كلام) لنسخة wxPython.

تُستخدم مكتبة ``pyttsx3`` التي تعتمد على محرّك النطق المثبّت في Windows
(SAPI5)، فتعمل **دون اتصال بالإنترنت** وتدعم اختيار الصوت والسرعة ومستوى
الصوت. يُدار المحرّك داخل خيط منفصل مع طابور أوامر حتى لا تتجمّد الواجهة.

التطبيق **يعمل بدون صوت** إذا لم يتوفّر محرّك النطق أو لم يوجد صوت عربي.
"""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass

from . import i18n


@dataclass(frozen=True)
class VoiceInfo:
    """معلومات صوت متاح على الجهاز."""

    id: str
    name: str
    language: str
    gender: str = ""


class NullSpeechService:
    """خدمة نطق صامتة تُستخدم عند غياب محرّك النطق."""

    def __init__(self) -> None:
        self.available = False
        self.reason_ar = ""
        self._last = ""

    def set_enabled(self, enabled: bool) -> None: ...
    def set_rate(self, rate: float) -> None: ...
    def set_volume(self, volume: float) -> None: ...
    def set_voice_name(self, name: str) -> None: ...
    def set_language(self, language: str) -> None: ...

    def say(self, text: str, language: str | None = None) -> None:
        self._last = text or ""

    def stop(self) -> None: ...
    def repeat(self) -> None:
        self.say(self._last)

    def voices(self) -> list[VoiceInfo]:
        return []

    def has_language(self, language: str) -> bool:
        return False

    def status_text(self) -> str:
        return self.reason_ar or i18n.t("speech_unavailable")

    @property
    def is_speaking(self) -> bool:
        return False

    @property
    def last_text(self) -> str:
        return self._last


class SpeechService:
    """خدمة نطق مبنية على ``pyttsx3`` تعمل في خيط منفصل."""

    def __init__(self) -> None:
        self.available = False
        self.reason_ar = ""
        self._enabled = False
        self._rate = 0.0
        self._volume = 1.0
        self._voice_name = ""
        self._language = ""
        self._last = ""
        self._voices: list[VoiceInfo] = []

        self._queue: "queue.Queue[tuple[str, object] | None]" = queue.Queue()
        self._ready = threading.Event()
        self._thread = threading.Thread(target=self._worker, name="braille-tts", daemon=True)
        self._thread.start()
        self._ready.wait(timeout=5.0)

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------
    def _worker(self) -> None:  # pragma: no cover - depends on pyttsx3
        engine = None
        try:
            import pyttsx3

            engine = pyttsx3.init()
            raw_voices = engine.getProperty("voices") or []
            for voice in raw_voices:
                languages = getattr(voice, "languages", None) or []
                lang = ""
                if languages:
                    first = languages[0]
                    lang = first.decode("utf-8", "ignore") if isinstance(first, bytes) else str(first)
                self._voices.append(
                    VoiceInfo(
                        id=str(getattr(voice, "id", "")),
                        name=str(getattr(voice, "name", "")),
                        language=lang,
                        gender=str(getattr(voice, "gender", "") or ""),
                    )
                )
            self.available = True
        except Exception as exc:  # pragma: no cover
            self.reason_ar = i18n.t("speech_engine_error", exc=exc)
            self.available = False
        self._ready.set()

        while True:
            item = self._queue.get()
            if item is None:
                break
            command, args = item
            if engine is None:
                continue
            try:
                self._handle(engine, command, args)
            except Exception:
                pass

    def _handle(self, engine, command: str, args) -> None:  # pragma: no cover
        if command == "say":
            text, language = args  # type: ignore[misc]
            if not text:
                return
            self._apply_engine_settings(engine, language)
            engine.say(text)
            engine.runAndWait()
        elif command == "stop":
            try:
                engine.stop()
            except Exception:
                pass
        elif command == "settings":
            self._apply_engine_settings(engine, self._language)

    def _apply_engine_settings(self, engine, language: str | None) -> None:  # pragma: no cover
        try:
            # pyttsx3 يقبل 50..400؛ نحوّل -1..1 إلى مدى معقول.
            words_per_minute = int(round(175 + self._rate * 125))
            engine.setProperty("rate", max(60, min(400, words_per_minute)))
        except Exception:
            pass
        try:
            engine.setProperty("volume", max(0.0, min(1.0, self._volume)))
        except Exception:
            pass
        wanted_voice = self._voice_name
        if not wanted_voice and (language or self._language):
            wanted_voice = self._voice_for_language(language or self._language)
        if wanted_voice:
            try:
                engine.setProperty("voice", wanted_voice)
            except Exception:
                pass

    def _voice_for_language(self, language: str) -> str:
        """أعد معرّف صوت يطابق اللغة المطلوبة إن وُجد."""
        if not language:
            return ""
        code = "ar" if language == "ar" else "en"
        for voice in self._voices:
            haystack = f"{voice.name} {voice.language} {voice.id}".lower()
            if code in haystack:
                return voice.id
        return ""

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = bool(enabled)
        if not enabled:
            self.stop()

    def set_rate(self, rate: float) -> None:
        self._rate = max(-1.0, min(1.0, float(rate)))

    def set_volume(self, volume: float) -> None:
        self._volume = max(0.0, min(1.0, float(volume)))

    def set_voice_name(self, name: str) -> None:
        self._voice_name = name or ""

    def set_language(self, language: str) -> None:
        self._language = language or ""

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    def voices(self) -> list[VoiceInfo]:
        return list(self._voices)

    def has_language(self, language: str) -> bool:
        code = "ar" if language == "ar" else "en"
        for voice in self._voices:
            haystack = f"{voice.name} {voice.language} {voice.id}".lower()
            if code in haystack:
                return True
        return False

    def status_text(self) -> str:
        if not self.available:
            return self.reason_ar or i18n.t("speech_not_available")
        if not self._voices:
            return i18n.t("speech_no_voices")
        if not self.has_language("ar"):
            return i18n.t("speech_no_arabic")
        return i18n.t("speech_available", count=len(self._voices))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def say(self, text: str, language: str | None = None) -> None:
        self._last = text or ""
        if not self.available or not self._enabled or not self._last:
            return
        self._queue.put(("say", (self._last, language)))

    def stop(self) -> None:
        if self.available:
            self._queue.put(("stop", None))

    def repeat(self) -> None:
        if self._last:
            self.say(self._last)

    @property
    def is_speaking(self) -> bool:
        return False

    @property
    def last_text(self) -> str:
        return self._last


def create_speech_service() -> SpeechService | NullSpeechService:
    """أنشئ خدمة النطق المناسبة بحسب ما هو متاح على الجهاز."""
    try:
        import pyttsx3  # noqa: F401
    except Exception:
        return NullSpeechService()
    service = SpeechService()
    if not service.available:
        return NullSpeechService()
    return service
