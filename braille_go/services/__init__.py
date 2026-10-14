"""الخدمات المساندة: النطق وإمكانية الوصول."""

from .accessibility import announce, describe_braille_cell, set_accessible
from .speech import NullSpeechService, SpeechService, create_speech_service

__all__ = [
    "announce",
    "describe_braille_cell",
    "set_accessible",
    "SpeechService",
    "NullSpeechService",
    "create_speech_service",
]
