"""إعدادات المستخدم: تحويلات قيمية وحفظ محلي.

Settings are stored as JSON-encoded values in the ``settings`` table of the
local SQLite database, so that a learner's preferences (font size, theme,
colours, sound, speech rate, mastery threshold, ...) are restored on the next
launch.  A small in-memory backend is provided as well so that the settings
model can be unit tested without touching the disk.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol

from .db import Database, DatabaseError


class SettingsError(RuntimeError):
    """خطأ في الإعدادات برسالة صديقة للمستخدم."""


class SettingsBackend(Protocol):
    """واجهة مخزن الإعدادات."""

    def load_all(self) -> dict[str, str]: ...

    def save(self, key: str, raw_value: str) -> None: ...

    def delete_all(self) -> None: ...


class SqliteSettingsBackend:
    """مخزن إعدادات مدعوم بقاعدة بيانات SQLite."""

    def __init__(self, database: Database) -> None:
        self._db = database

    def load_all(self) -> dict[str, str]:
        rows = self._db.query("SELECT key, value FROM settings")
        return {row["key"]: row["value"] for row in rows}

    def save(self, key: str, raw_value: str) -> None:
        self._db.execute(
            "INSERT INTO settings(key, value, updated_at) VALUES(?, ?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
            "updated_at = excluded.updated_at",
            (key, raw_value, _now()),
        )

    def delete_all(self) -> None:
        self._db.execute("DELETE FROM settings")


class MemorySettingsBackend:
    """مخزن إعدادات في الذاكرة (للاختبارات)."""

    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self._data: dict[str, str] = dict(initial or {})

    def load_all(self) -> dict[str, str]:
        return dict(self._data)

    def save(self, key: str, raw_value: str) -> None:
        self._data[key] = raw_value

    def delete_all(self) -> None:
        self._data.clear()


#: القيم الافتراضية لكل الإعدادات المدعومة.
DEFAULT_SETTINGS: dict[str, Any] = {
    # العرض
    "font_scale": 1.0,
    "braille_cell_scale": 1.0,
    "theme": "light",                # light | dark
    "display_mode": "normal_light",  # نمط عرض جاهز (انظر ui/theme في نسخة wx)
    "bold_text": False,
    "line_spacing": 1.0,
    "high_contrast": False,
    "reduce_motion": False,
    "text_color": "",                # فارغ = اتبع الثيم
    "background_color": "",
    "dot_color": "#1a1a1a",
    "dot_empty_color": "#c9c9c9",
    "dot_border_color": "#4a4a4a",
    # الأصوات والنطق
    "sound_enabled": True,
    "speech_enabled": False,
    "speech_rate": 0.0,              # -1.0 (بطيء) .. 1.0 (سريع)
    "volume": 1.0,                   # 0.0 .. 1.0
    "speech_voice": "",              # اسم الصوت إن وُجد
    "speech_locale": "",             # ar | en | فارغ = تلقائي
    "guidance_enabled": True,        # الإرشادات الصوتية للتطبيق
    # التعلّم
    "mastery_threshold": 85.0,       # نسبة الإتقان المطلوبة للانتقال
    "auto_confirm_answer": False,
    "show_dot_numbers": True,
    "interface_language": "ar",      # ar (قابل للتوسّع)
    "guided_mode": True,             # وضع التعلم الإرشادي للمبتدئين
    "show_large_target": True,       # عرض المطلوب تعلمه بحجم كبير
    "welcome_shown": False,          # هل عُرضت شاشة الترحيب من قبل
    # سلوك
    "last_lesson_key": "",
    "last_level_key": "",
}

#: إعدادات منطقية، تُستخدم في التحقق من النوع.
_BOOL_KEYS = {
    "high_contrast", "reduce_motion", "sound_enabled", "speech_enabled",
    "guidance_enabled", "auto_confirm_answer", "show_dot_numbers",
    "bold_text", "guided_mode", "show_large_target", "welcome_shown",
}
_FLOAT_KEYS = {"font_scale", "braille_cell_scale", "speech_rate", "volume", "mastery_threshold", "line_spacing"}
_INT_KEYS: set[str] = set()
_STR_KEYS = {
    "theme", "display_mode", "text_color", "background_color", "dot_color", "dot_empty_color",
    "dot_border_color", "speech_voice", "speech_locale", "interface_language",
    "last_lesson_key", "last_level_key",
}

#: حدود مقبولة لكل مفتاح عددي.
_NUMERIC_BOUNDS: dict[str, tuple[float, float]] = {
    "font_scale": (0.6, 3.0),
    "braille_cell_scale": (0.6, 3.0),
    "speech_rate": (-1.0, 1.0),
    "volume": (0.0, 1.0),
    "mastery_threshold": (0.0, 100.0),
    "line_spacing": (0.8, 3.0),
}

#: القيم المسموحة للثيم.
VALID_THEMES = ("light", "dark")


def _now() -> str:
    from .db import utc_now

    return utc_now()


@dataclass
class SettingSpec:
    """وصف إعداد واحد (يُستخدم في بناء واجهة الإعدادات أيضًا)."""

    key: str
    label_ar: str
    kind: str  # "bool" | "float" | "int" | "choice" | "color" | "text"
    description_ar: str = ""
    choices: tuple[tuple[str, str], ...] = ()  # (value, label)


SETTING_SPECS: tuple[SettingSpec, ...] = (
    SettingSpec("font_scale", "حجم الخط", "float", "تكبير أو تصغير حجم نص الواجهة."),
    SettingSpec("braille_cell_scale", "حجم خلايا برايل", "float", "تكبير أو تصغير حجم خلية برايل."),
    SettingSpec(
        "theme", "الوضع", "choice", "اختيار الوضع الفاتح أو الداكن.",
        choices=(("light", "فاتح"), ("dark", "داكن")),
    ),
    SettingSpec("high_contrast", "وضع التباين المرتفع", "bool", "زيادة التباين لضعاف البصر."),
    SettingSpec("reduce_motion", "تقليل الحركات والمؤثرات", "bool", "إيقاف المؤثرات البصرية المتحركة."),
    SettingSpec("text_color", "لون النص", "color", "اتركه فارغًا لاستخدام لون الوضع."),
    SettingSpec("background_color", "لون الخلفية", "color", "اتركه فارغًا لاستخدام لون الوضع."),
    SettingSpec("dot_color", "لون النقاط المحدّدة", "color"),
    SettingSpec("dot_empty_color", "لون النقاط غير المحدّدة", "color"),
    SettingSpec("sound_enabled", "تشغيل الأصوات", "bool", "أصوات التنبيه والتفاعل."),
    SettingSpec("speech_enabled", "تشغيل النطق", "bool", "تحويل النص والحروف إلى كلام."),
    SettingSpec("guidance_enabled", "الإرشادات الصوتية", "bool", "نطق التعليمات تلقائيًا عند فتح السؤال."),
    SettingSpec("volume", "مستوى الصوت", "float"),
    SettingSpec("speech_rate", "سرعة النطق", "float"),
    SettingSpec("show_dot_numbers", "إظهار أرقام النقاط", "bool", "عرض الرقم على كل نقطة في الخلية."),
    SettingSpec("mastery_threshold", "نسبة الإتقان المطلوبة", "float", "النسبة اللازمة للانتقال إلى المستوى التالي (الافتراضي 85%)."),
)


class Settings:
    """نموذج الإعدادات مع استعادة وحفظ تلقائي."""

    def __init__(self, backend: SettingsBackend) -> None:
        self._backend = backend
        self._values: dict[str, Any] = dict(DEFAULT_SETTINGS)
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        try:
            stored = self._backend.load_all()
        except DatabaseError:
            # لا نُفشل التطبيق إذا تعذّرت قراءة الإعدادات؛ نستخدم الافتراضي.
            stored = {}
        for key, raw in stored.items():
            if key not in DEFAULT_SETTINGS:
                continue
            self._values[key] = _decode(key, raw)

    def save(self, key: str | None = None) -> None:
        """احفظ إعدادًا واحدًا أو كل الإعدادات."""
        keys = [key] if key else list(self._values)
        try:
            for item in keys:
                if item in self._values:
                    self._backend.save(item, json.dumps(self._values[item], ensure_ascii=False))
        except DatabaseError as exc:
            raise SettingsError(f"تعذّر حفظ الإعدادات: {exc}") from exc

    # ------------------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        if key in self._values:
            return self._values[key]
        return DEFAULT_SETTINGS.get(key, default)

    def set(self, key: str, value: Any, persist: bool = True) -> Any:
        """عيّن قيمة إعداد مع التحقق من النوع، ثم احفظها."""
        if key not in DEFAULT_SETTINGS:
            raise SettingsError(f"إعداد غير معروف: {key}")
        coerced = _coerce(key, value)
        self._values[key] = coerced
        if persist:
            self.save(key)
        return coerced

    def update(self, values: dict[str, Any], persist: bool = True) -> None:
        for key, value in values.items():
            self.set(key, value, persist=False)
        if persist:
            self.save()

    def reset(self) -> None:
        """أعد كل الإعدادات إلى القيم الافتراضية."""
        self._values = dict(DEFAULT_SETTINGS)
        try:
            self._backend.delete_all()
        except DatabaseError as exc:
            raise SettingsError(f"تعذّر إعادة ضبط الإعدادات: {exc}") from exc
        self.save()

    def as_dict(self) -> dict[str, Any]:
        return dict(self._values)

    # ------------------------------------------------------------------
    # خصائص مريحة
    # ------------------------------------------------------------------
    @property
    def mastery_threshold(self) -> float:
        return float(self._values["mastery_threshold"])

    @property
    def font_scale(self) -> float:
        return float(self._values["font_scale"])

    @property
    def braille_cell_scale(self) -> float:
        return float(self._values["braille_cell_scale"])

    @property
    def theme(self) -> str:
        return str(self._values["theme"])

    @property
    def dark_mode(self) -> bool:
        return self._values["theme"] == "dark"

    @property
    def high_contrast(self) -> bool:
        return bool(self._values["high_contrast"])

    @property
    def speech_enabled(self) -> bool:
        return bool(self._values["speech_enabled"])

    @property
    def sound_enabled(self) -> bool:
        return bool(self._values["sound_enabled"])

    @property
    def reduce_motion(self) -> bool:
        return bool(self._values["reduce_motion"])


def _decode(key: str, raw: str) -> Any:
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return DEFAULT_SETTINGS[key]
    try:
        return _coerce(key, value)
    except SettingsError:
        return DEFAULT_SETTINGS[key]


def _coerce(key: str, value: Any) -> Any:
    default = DEFAULT_SETTINGS[key]
    if key in _BOOL_KEYS:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on", "نعم", "صح"}
        return bool(default)
    if key in _FLOAT_KEYS:
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise SettingsError(f"قيمة غير رقمية للإعداد {key}: {value!r}")
        low, high = _NUMERIC_BOUNDS.get(key, (float("-inf"), float("inf")))
        return max(low, min(high, number))
    if key in _INT_KEYS:
        try:
            return int(value)
        except (TypeError, ValueError):
            raise SettingsError(f"قيمة غير صحيحة للإعداد {key}: {value!r}")
    if key in _STR_KEYS:
        text = "" if value is None else str(value)
        if key == "theme" and text not in VALID_THEMES:
            return default
        if key in {"text_color", "background_color", "dot_color", "dot_empty_color", "dot_border_color"}:
            text = text.strip()
        return text
    return value
