"""فئات المستخدمين في Braille Go.

يحدّد المستخدم في الإعدادات فئته، فيبدأ التطبيق بإعدادات مقترحة مناسبة له
(ويمكنه بعد ذلك تعديلها يدويًا). الفئات الأربع مبنية على تعليمات المراجعة:

* ``instructor``        — مدرب في مركز أو مؤسسة.
* ``sighted_learner``   — متدرب مبصر يتعلّم أساسيات برايل.
* ``blind``             — متعلّم كفيف يعتمد على قارئ الشاشة والنطق.
* ``low_vision``        — متعلّم ضعيف بصر يحتاج تباينًا وتكبيرًا.

كل فئة تقترح: نمط العرض، حجم الخط، حجم خلية برايل، النص العريض، النطق
والإرشادات والأصوات، وأرقام النقاط، ووضع المدرب.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class UserProfile:
    """فئة مستخدم مع الإعدادات المقترحة لها."""

    key: str
    label_key: str
    description_key: str
    settings: dict[str, Any]
    icon: str = ""


#: الفئات الأربع بالترتيب الذي تظهر به في الإعدادات.
PROFILES: dict[str, UserProfile] = {
    "instructor": UserProfile(
        key="instructor",
        label_key="profile_instructor",
        description_key="profile_instructor_desc",
        icon="🧑‍🏫",
        settings={
            "instructor_mode": True,
            "display_mode": "normal_light",
            "font_scale": 1.15,
            "braille_cell_scale": 1.2,
            "bold_text": True,
            "show_dot_numbers": True,
            "speech_enabled": False,
            "guidance_enabled": False,
            "sound_enabled": True,
            "encouragement_enabled": True,
            "announce_symbols": True,
            "guided_mode": False,
            "show_large_target": True,
        },
    ),
    "sighted_learner": UserProfile(
        key="sighted_learner",
        label_key="profile_sighted",
        description_key="profile_sighted_desc",
        icon="👀",
        settings={
            "instructor_mode": False,
            "display_mode": "normal_light",
            "font_scale": 1.0,
            "braille_cell_scale": 1.3,
            "bold_text": False,
            "show_dot_numbers": True,
            "speech_enabled": False,
            "guidance_enabled": True,
            "sound_enabled": True,
            "encouragement_enabled": True,
            "announce_symbols": True,
            "guided_mode": True,
            "show_large_target": True,
        },
    ),
    "blind": UserProfile(
        key="blind",
        label_key="profile_blind",
        description_key="profile_blind_desc",
        icon="🔊",
        settings={
            "instructor_mode": False,
            "display_mode": "hc_dark",
            "font_scale": 1.5,
            "braille_cell_scale": 2.0,
            "bold_text": True,
            "show_dot_numbers": True,
            "speech_enabled": True,
            "guidance_enabled": True,
            "sound_enabled": True,
            "encouragement_enabled": True,
            "announce_symbols": True,
            "guided_mode": True,
            "show_large_target": True,
            "reduce_motion": False,
        },
    ),
    "low_vision": UserProfile(
        key="low_vision",
        label_key="profile_low_vision",
        description_key="profile_low_vision_desc",
        icon="🔍",
        settings={
            "instructor_mode": False,
            "display_mode": "yellow_black",
            "font_scale": 1.9,
            "braille_cell_scale": 2.2,
            "bold_text": True,
            "show_dot_numbers": True,
            "speech_enabled": True,
            "guidance_enabled": True,
            "sound_enabled": True,
            "encouragement_enabled": True,
            "announce_symbols": True,
            "guided_mode": True,
            "show_large_target": True,
        },
    ),
}

#: ترتيب العرض.
PROFILE_ORDER: tuple[str, ...] = ("instructor", "sighted_learner", "blind", "low_vision")

#: الفئة الافتراضية.
DEFAULT_PROFILE = "sighted_learner"


def profile_choices() -> list[tuple[str, str, str]]:
    """قائمة ``(المفتاح، التسمية، الوصف)`` باللغة الحالية."""
    from . import i18n

    result: list[tuple[str, str, str]] = []
    for key in PROFILE_ORDER:
        profile = PROFILES[key]
        result.append((key, i18n.t(profile.label_key), i18n.t(profile.description_key)))
    return result


def profile_settings(key: str) -> dict[str, Any]:
    """الإعدادات المقترحة لفئة، أو نسخة فارغة إن كانت غير معروفة."""
    profile = PROFILES.get(key)
    return dict(profile.settings) if profile else {}


def apply_profile(settings, key: str) -> None:
    """طبّق الإعدادات المقترحة لفئة مع حفظها."""
    values = profile_settings(key)
    values["user_profile"] = key
    settings.update(values)


__all__ = [
    "PROFILES",
    "PROFILE_ORDER",
    "DEFAULT_PROFILE",
    "UserProfile",
    "profile_choices",
    "profile_settings",
    "apply_profile",
]
