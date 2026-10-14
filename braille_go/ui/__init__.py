"""طبقة الواجهة الرسومية (PySide6).

The GUI is split into small modules so that the braille data, the exercise
engine and the progress rules stay completely independent from Qt:

* :mod:`~braille_go.ui.theme`  — الألوان والخطوط والتباين.
* :mod:`~braille_go.ui.widgets` — عناصر مشتركة.
* :mod:`~braille_go.ui.braille_cell_widget` — خلية برايل التفاعلية.
* :mod:`~braille_go.ui.exercise_widget` — مشغّل التدريبات والتغذية الراجعة.
* :mod:`~braille_go.ui.screens` — شاشات التطبيق.
* :mod:`~braille_go.ui.main_window` — النافذة الرئيسية والتنقل.
"""

from .main_window import MainWindow

__all__ = ["MainWindow"]
