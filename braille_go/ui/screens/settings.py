"""شاشة الإعدادات والتخصيص."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from ..widgets import Card, body_label, button, StatusBanner
from .base import BaseScreen


def _line_edit(initial: str = "") -> QLineEdit:
    w = QLineEdit(initial)
    w.setAccessibleName("حقل نص")
    return w


class SettingsScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="الإعدادات والتخصيص")
        self.setLayoutDirection(Qt.RightToLeft)

        self._banner = StatusBanner()
        self.layout.addWidget(self._banner)

        # Display
        disp = Card("العرض والخطوط")
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(6)

        grid.addWidget(QLabel("حجم الخط"), 0, 0)
        self._font = QDoubleSpinBox()
        self._font.setRange(0.6, 3.0)
        self._font.setSingleStep(0.05)
        self._font.setDecimals(2)
        grid.addWidget(self._font, 0, 1)

        grid.addWidget(QLabel("حجم خلايا برايل"), 1, 0)
        self._cell_scale = QDoubleSpinBox()
        self._cell_scale.setRange(0.6, 3.0)
        self._cell_scale.setSingleStep(0.05)
        self._cell_scale.setDecimals(2)
        grid.addWidget(self._cell_scale, 1, 1)

        grid.addWidget(QLabel("الوضع"), 2, 0)
        self._theme = QComboBox()
        self._theme.addItem("فاتح", "light")
        self._theme.addItem("داكن", "dark")
        grid.addWidget(self._theme, 2, 1)

        grid.addWidget(QLabel("وضع التباين المرتفع"), 3, 0)
        self._high_contrast = QCheckBox("تفعيل")
        grid.addWidget(self._high_contrast, 3, 1)

        grid.addWidget(QLabel("تقليل الحركات والمؤثرات"), 4, 0)
        self._reduce_motion = QCheckBox("تفعيل")
        grid.addWidget(self._reduce_motion, 4, 1)

        grid.addWidget(QLabel("إظهار أرقام النقاط"), 5, 0)
        self._dot_nums = QCheckBox("تفعيل")
        grid.addWidget(self._dot_nums, 5, 1)

        disp.add_layout(grid)
        self.layout.addWidget(disp)

        # Colors
        colors = Card("ألوان مخصّصة (اترك فارغًا لاستخدام الثيم)")
        cgrid = QGridLayout()
        cgrid.addWidget(QLabel("لون النص"), 0, 0)
        self._text_color = _line_edit()
        cgrid.addWidget(self._text_color, 0, 1)
        cgrid.addWidget(QLabel("لون الخلفية"), 1, 0)
        self._bg_color = _line_edit()
        cgrid.addWidget(self._bg_color, 1, 1)
        cgrid.addWidget(QLabel("لون النقاط المحدّدة"), 2, 0)
        self._dot_on = _line_edit()
        cgrid.addWidget(self._dot_on, 2, 1)
        cgrid.addWidget(QLabel("لون النقاط غير المحدّدة"), 3, 0)
        self._dot_off = _line_edit()
        cgrid.addWidget(self._dot_off, 3, 1)
        colors.add_layout(cgrid)
        self.layout.addWidget(colors)

        # Sound
        sound = Card("الصوت والنطق")
        sgrid = QGridLayout()
        sgrid.addWidget(QLabel("تشغيل الأصوات"), 0, 0)
        self._sound = QCheckBox("تفعيل")
        sgrid.addWidget(self._sound, 0, 1)
        sgrid.addWidget(QLabel("تشغيل النطق"), 1, 0)
        self._speech = QCheckBox("تفعيل")
        sgrid.addWidget(self._speech, 1, 1)
        sgrid.addWidget(QLabel("الإرشادات الصوتية"), 2, 0)
        self._guidance = QCheckBox("تفعيل")
        sgrid.addWidget(self._guidance, 2, 1)
        sgrid.addWidget(QLabel("مستوى الصوت"), 3, 0)
        self._volume = QDoubleSpinBox()
        self._volume.setRange(0.0, 1.0)
        self._volume.setSingleStep(0.05)
        self._volume.setDecimals(2)
        sgrid.addWidget(self._volume, 3, 1)
        sgrid.addWidget(QLabel("سرعة النطق"), 4, 0)
        self._rate = QDoubleSpinBox()
        self._rate.setRange(-1.0, 1.0)
        self._rate.setSingleStep(0.05)
        self._rate.setDecimals(2)
        sgrid.addWidget(self._rate, 4, 1)
        sgrid.addWidget(QLabel("نسبة الإتقان المطلوبة"), 5, 0)
        self._mastery = QDoubleSpinBox()
        self._mastery.setRange(0.0, 100.0)
        self._mastery.setSingleStep(0.5)
        self._mastery.setDecimals(1)
        self._mastery.setSuffix(" %")
        sgrid.addWidget(self._mastery, 5, 1)
        sound.add_layout(sgrid)
        sound.add(body_label(self.context.speech_status(), wrap=True))
        self.layout.addWidget(sound)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch(1)
        self._btn_apply = button("حفظ الإعدادات", primary=True, on_click=self._apply)
        self._btn_reset = button("إعادة ضبط الافتراضي", danger=True, on_click=self._reset)
        btns.addWidget(self._btn_apply)
        btns.addWidget(self._btn_reset)
        self.layout.addLayout(btns)
        self.layout.addStretch(1)

    def activate(self, **kwargs) -> None:
        s = self.context.settings
        self._font.setValue(s.get("font_scale", 1.0))
        self._cell_scale.setValue(s.get("braille_cell_scale", 1.0))
        idx = self._theme.findData(s.get("theme", "light"))
        if idx >= 0:
            self._theme.setCurrentIndex(idx)
        self._high_contrast.setChecked(bool(s.get("high_contrast", False)))
        self._reduce_motion.setChecked(bool(s.get("reduce_motion", False)))
        self._dot_nums.setChecked(bool(s.get("show_dot_numbers", True)))
        self._text_color.setText(str(s.get("text_color", "")))
        self._bg_color.setText(str(s.get("background_color", "")))
        self._dot_on.setText(str(s.get("dot_color", "")))
        self._dot_off.setText(str(s.get("dot_empty_color", "")))
        self._sound.setChecked(bool(s.get("sound_enabled", True)))
        self._speech.setChecked(bool(s.get("speech_enabled", False)))
        self._guidance.setChecked(bool(s.get("guidance_enabled", True)))
        self._volume.setValue(s.get("volume", 1.0))
        self._rate.setValue(s.get("speech_rate", 0.0))
        self._mastery.setValue(s.get("mastery_threshold", 85.0))
        self._banner.setVisible(False)

    def _apply(self) -> None:
        s = self.context.settings
        s.set("font_scale", self._font.value())
        s.set("braille_cell_scale", self._cell_scale.value())
        data = self._theme.currentData()
        s.set("theme", data if data else "light")
        s.set("high_contrast", self._high_contrast.isChecked())
        s.set("reduce_motion", self._reduce_motion.isChecked())
        s.set("show_dot_numbers", self._dot_nums.isChecked())
        s.set("text_color", self._text_color.text())
        s.set("background_color", self._bg_color.text())
        s.set("dot_color", self._dot_on.text())
        s.set("dot_empty_color", self._dot_off.text())
        s.set("sound_enabled", self._sound.isChecked())
        s.set("speech_enabled", self._speech.isChecked())
        s.set("guidance_enabled", self._guidance.isChecked())
        s.set("volume", self._volume.value())
        s.set("speech_rate", self._rate.value())
        s.set("mastery_threshold", self._mastery.value())
        from PySide6.QtWidgets import QApplication
        from ..theme import apply_theme

        apply_theme(QApplication.instance(), s)
        self.context.apply_settings()
        self._banner.show_message("تم حفظ الإعدادات بنجاح.", tone="ok")

    def _reset(self) -> None:
        from ..widgets import confirm

        if confirm(self, "إعادة الضبط", "هل تريد إعادة جميع الإعدادات إلى القيم الافتراضية؟"):
            self.context.reset_settings()
            from PySide6.QtWidgets import QApplication
            from ..theme import apply_theme

            apply_theme(QApplication.instance(), self.context.settings)
            self.activate()
            self._banner.show_message("تمت إعادة الإعدادات إلى الافتراضي.", tone="ok")
