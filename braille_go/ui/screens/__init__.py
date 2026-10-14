"""شاشات الواجهة الرئيسية."""

from .base import BaseScreen, base_screen, route
from .exams import ExamsScreen
from .help import HelpScreen
from .home import HomeScreen
from .lesson import LessonScreen
from .lessons import LessonsScreen
from .practice import PracticeScreen
from .progress import ProgressScreen
from .review import ReviewScreen
from .settings import SettingsScreen

__all__ = [
    "BaseScreen",
    "base_screen",
    "route",
    "ExamsScreen",
    "HelpScreen",
    "HomeScreen",
    "LessonScreen",
    "LessonsScreen",
    "PracticeScreen",
    "ProgressScreen",
    "ReviewScreen",
    "SettingsScreen",
]
