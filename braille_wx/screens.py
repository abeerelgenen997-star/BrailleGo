"""شاشات التطبيق (ما عدا شاشة الدرس) لنسخة wxPython."""

from __future__ import annotations

import csv
from datetime import datetime

import wx

from braille_go.core.curriculum import LEVELS, LEVELS_BY_KEY, first_lesson, level_of_lesson

from . import i18n
from . import theme as theme_mod
from . import widgets as W
from .base_panel import BasePanel, clear_sizer


# ----------------------------------------------------------------------
# الترحيب
# ----------------------------------------------------------------------
class WelcomePanel(BasePanel):
    """شاشة الترحيب: تُعرض مرة واحدة عند أول تشغيل، وتنطق ترحيبًا ثم تُكمل."""

    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        clear_sizer(self.content)
        self.content.AddStretchSpacer(1)
        title = wx.StaticText(self, label=i18n.t("welcome"))
        title.SetName(i18n.t("welcome"))
        try:
            font = self.theme.make_font(34.0)
            font.SetWeight(wx.FONTWEIGHT_BOLD)
            title.SetFont(font)
        except Exception:
            pass
        self.content.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 20)

        subtitle = wx.StaticText(self, label=i18n.t("welcome_subtitle"))
        subtitle.SetName(i18n.t("welcome_subtitle"))
        self.content.Add(subtitle, 0, wx.ALIGN_CENTER | wx.ALL, 12)

        self._button = W.action_button(
            self, i18n.t("start_learning"), primary=True,
            on_click=self._go_home, tooltip="Ctrl+Enter",
        )
        self.content.Add(self._button, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.content.AddStretchSpacer(1)
        self._timer: wx.Timer | None = None
        self.finish_layout()

    def activate(self, **kwargs) -> None:
        try:
            self.context.speak(i18n.t("welcome_speak"), self.context.settings.get("speech_locale") or None)
        except Exception:
            pass
        try:
            self.context.settings.set("welcome_shown", True)
        except Exception:
            pass
        if self._button is not None:
            self._button.SetFocus()
        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda event: self._go_home(), self._timer)
        self._timer.StartOnce(3500)

    def deactivate(self) -> None:
        if self._timer is not None:
            self._timer.Stop()

    def _go_home(self) -> None:
        if self._timer is not None:
            self._timer.Stop()
        self.frame.navigate_to("home")

    def confirm_action(self) -> bool:
        self._go_home()
        return True


# ----------------------------------------------------------------------
# الرئيسية
# ----------------------------------------------------------------------
class HomePanel(BasePanel):
    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        clear_sizer(self.content)
        self.content.Add(W.heading(self, "Braille Go", self.theme), 0, wx.ALL, 8)
        self.content.Add(
            W.wrapped_text(
                self,
                "تطبيق تعليمي تفاعلي لتعلّم طريقة برايل العربي والإنجليزي، مع نظام "
                "مستويات وتقدّم محفوظ محليًا، وواجهة تعمل دون اتصال بالإنترنت.",
            ),
            0, wx.EXPAND | wx.ALL, 10,
        )

        row = wx.BoxSizer(wx.HORIZONTAL)
        self.content.Add(row, 0, wx.EXPAND | wx.ALL, 6)

        learn, lsizer = W.card(self, row, "التعلّم")
        lsizer.Add(W.action_button(learn, i18n.t("start_learning"), primary=True, on_click=self._start), 0, wx.EXPAND | wx.ALL, 4)
        lsizer.Add(W.action_button(learn, i18n.t("continue_last"), on_click=self._continue), 0, wx.EXPAND | wx.ALL, 4)
        lsizer.Add(W.action_button(learn, i18n.t("lessons_levels"), on_click=lambda: self.frame.navigate_to("lessons")), 0, wx.EXPAND | wx.ALL, 4)

        practice, psizer = W.card(self, row, "التدريب")
        psizer.Add(W.action_button(practice, "التدريب العام", on_click=lambda: self.frame.navigate_to("practice")), 0, wx.EXPAND | wx.ALL, 4)
        psizer.Add(W.action_button(practice, i18n.t("exams"), on_click=lambda: self.frame.navigate_to("exams")), 0, wx.EXPAND | wx.ALL, 4)
        psizer.Add(W.action_button(practice, i18n.t("review_errors"), on_click=lambda: self.frame.navigate_to("review")), 0, wx.EXPAND | wx.ALL, 4)

        track, tsizer = W.card(self, row, "المتابعة")
        tsizer.Add(W.action_button(track, i18n.t("progress"), on_click=lambda: self.frame.navigate_to("progress")), 0, wx.EXPAND | wx.ALL, 4)
        tsizer.Add(W.action_button(track, i18n.t("instructor"), on_click=lambda: self.frame.navigate_to("instructor")), 0, wx.EXPAND | wx.ALL, 4)
        tsizer.Add(W.action_button(track, i18n.t("settings"), on_click=lambda: self.frame.navigate_to("settings")), 0, wx.EXPAND | wx.ALL, 4)
        tsizer.Add(W.action_button(track, i18n.t("help"), on_click=lambda: self.frame.navigate_to("help")), 0, wx.EXPAND | wx.ALL, 4)

        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _start(self) -> None:
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "")

    def _continue(self) -> None:
        lesson = self.context.last_lesson()
        level = level_of_lesson(lesson.key)
        self.frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "")

    def focus_edit_box(self) -> bool:
        return False


# ----------------------------------------------------------------------
# الدروس والمستويات
# ----------------------------------------------------------------------
class LessonsPanel(BasePanel):
    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        self._built = False

    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("lessons_levels"), self.theme), 0, wx.ALL, 8)
        for level in LEVELS:
            unlocked = self.context.is_level_unlocked(level.key)
            evaluation = self.context.evaluate(level)
            panel, sizer = W.card(self, self.content, f"{level.number}. {level.title_ar}")
            sizer.Add(W.wrapped_text(
                panel,
                f"{level.description_ar}\nمكتمل: {evaluation.lessons_completed}/{evaluation.lessons_total} — "
                f"إتقان: {int(round(evaluation.mastery))}%",
            ), 0, wx.EXPAND | wx.ALL, 4)
            for lesson in level.lessons:
                result = self.context.progress.lesson_result(lesson.key)
                completed = bool(result and result.completed)
                attempted = bool(result and result.attempts > 0)
                status = "✓ مكتمل" if completed else ("مُجرَّب" if attempted else "جديد")
                button = W.action_button(
                    panel,
                    f"{lesson.title_ar} — {status}",
                    on_click=lambda lk=lesson.key, lv=level.key: self.frame.navigate_to("lesson", lesson_key=lk, level_key=lv),
                    enabled=unlocked,
                    tooltip=lesson.description_ar,
                )
                sizer.Add(button, 0, wx.EXPAND | wx.ALL, 3)
            if not unlocked:
                sizer.Add(W.body(panel, "يُفتح هذا المستوى بعد إتقان المستوى السابق."), 0, wx.ALL, 3)
        self.content.AddStretchSpacer(1)
        self.finish_layout()


# ----------------------------------------------------------------------
# التدريب
# ----------------------------------------------------------------------
class PracticePanel(BasePanel):
    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        clear_sizer(self.content)
        self.content.Add(W.heading(self, "التدريب العام", self.theme), 0, wx.ALL, 8)

        panel, sizer = W.card(self, self.content, "مراجعة مركّزة")
        sizer.Add(W.wrapped_text(panel, "مراجعة على الرموز الأكثر خطأً لديك، وإن لم توجد أخطاء فتدريب عام."), 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(W.action_button(panel, "ابدأ تدريب المراجعة", primary=True, on_click=self._review), 0, wx.ALL, 4)

        panel2, sizer2 = W.card(self, self.content, "تدريب عشوائي مختلط")
        sizer2.Add(W.wrapped_text(panel2, "تدريب مختلط من أول درس متاح."), 0, wx.EXPAND | wx.ALL, 4)
        sizer2.Add(W.action_button(panel2, "ابدأ تدريب عشوائي", on_click=self._mixed), 0, wx.ALL, 4)
        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _review(self) -> None:
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "", mode="review")

    def _mixed(self) -> None:
        lesson = first_lesson()
        level = level_of_lesson(lesson.key)
        self.frame.navigate_to("lesson", lesson_key=lesson.key, level_key=level.key if level else "", mode="mixed")


# ----------------------------------------------------------------------
# الاختبارات
# ----------------------------------------------------------------------
class ExamsPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("exams"), self.theme), 0, wx.ALL, 8)
        panel, sizer = W.card(self, self.content, "اختبارات المستويات")
        sizer.Add(W.wrapped_text(panel, "اختر مستوى لتقدّم لاختباره (وفق شروط الإتقان)."), 0, wx.EXPAND | wx.ALL, 4)
        for level in LEVELS:
            evaluation = self.context.evaluate(level)
            unlocked = self.context.is_level_unlocked(level.key)
            exam_key = self._exam_lesson(level.key)
            sizer.Add(W.action_button(
                panel,
                f"المستوى {level.number}: {level.title_ar} — إتقان {int(round(evaluation.mastery))}%",
                on_click=lambda lk=exam_key, lv=level.key: self.frame.navigate_to("lesson", lesson_key=lk, level_key=lv, mode="exam"),
                enabled=unlocked,
            ), 0, wx.EXPAND | wx.ALL, 3)
        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _exam_lesson(self, level_key: str) -> str:
        level = LEVELS_BY_KEY.get(level_key)
        if not level:
            return ""
        for lesson in level.lessons:
            if lesson.is_exam:
                return lesson.key
        return level.lessons[-1].key if level.lessons else ""


# ----------------------------------------------------------------------
# مراجعة الأخطاء
# ----------------------------------------------------------------------
class ReviewPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, "مراجعة الأخطاء السابقة", self.theme), 0, wx.ALL, 8)
        wrong = self.context.progress.wrong_answers(limit=30)
        if not wrong:
            panel, sizer = W.card(self, self.content, "لا توجد أخطاء محفوظة بعد")
            sizer.Add(W.wrapped_text(panel, "بعد الإجابة على التدريبات ستظهر هنا قائمة الأخطاء."), 0, wx.EXPAND | wx.ALL, 4)
        else:
            for row in wrong:
                panel, sizer = W.card(self, self.content, str(row["lesson_key"]))
                text = (
                    f"التاريخ: {row['created_at']}\n"
                    f"نوع التدريب: {row['kind']}\n"
                    f"الرموز: {row['symbol_keys']}\n"
                    f"ما أجبت به: {row['given']}\n"
                    f"الإجابة الصحيحة: {row['expected']}"
                )
                sizer.Add(W.wrapped_text(panel, text), 0, wx.EXPAND | wx.ALL, 4)
        self.content.AddStretchSpacer(1)
        self.finish_layout()


# ----------------------------------------------------------------------
# التقدّم
# ----------------------------------------------------------------------
class ProgressPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("progress"), self.theme), 0, wx.ALL, 8)
        stats = self.context.progress.statistics()
        gauge = wx.Gauge(self, range=100)
        gauge.SetValue(int(round(float(stats["accuracy"]))))
        gauge.SetName(f"التقدّم العام {int(round(float(stats['accuracy'])))} بالمئة")
        self.content.Add(gauge, 0, wx.EXPAND | wx.ALL, 8)
        self.content.Add(W.body(
            self,
            f"إجابات صحيحة: {stats['answers_correct']}/{stats['answers_total']} — "
            f"دروس جُرّبت: {stats['lessons_attempted']} — مكتملة: {stats['lessons_completed']} — "
            f"الإتقان المطلوب: {int(round(self.context.mastery_threshold))}%",
        ), 0, wx.EXPAND | wx.ALL, 8)

        for level in LEVELS:
            evaluation = self.context.evaluate(level)
            panel, sizer = W.card(self, self.content, f"المستوى {level.number}: {evaluation.mastery:.0f}%")
            sizer.Add(W.wrapped_text(
                panel,
                f"مكتمل {evaluation.lessons_completed}/{evaluation.lessons_total}. {evaluation.reason_ar}",
            ), 0, wx.EXPAND | wx.ALL, 4)

        self.content.Add(W.action_button(self, "إعادة ضبط كل التقدّم", on_click=self._reset), 0, wx.ALL, 8)
        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _reset(self) -> None:
        if W.confirm(self, "تأكيد إعادة الضبط", "هل تريد حذف كل بيانات التقدّم؟ لا يمكن التراجع."):
            self.context.progress.reset_all()
            self.activate()
            self.frame.refresh_status()


# ----------------------------------------------------------------------
# الإعدادات (غنية بأنماط العرض)
# ----------------------------------------------------------------------
class SettingsPanel(BasePanel):
    def __init__(self, parent: wx.Window, context, frame) -> None:
        super().__init__(parent, context, frame)
        self._building = True
        self._build()
        self._building = False

    def _build(self) -> None:
        clear_sizer(self.content)
        s = self.context.settings

        self.content.Add(W.heading(self, i18n.t("settings"), self.theme), 0, wx.ALL, 8)

        # أنماط العرض --------------------------------------------------
        panel, sizer = W.card(self, self.content, i18n.t("display_mode"))
        sizer.Add(W.wrapped_text(panel, i18n.t("display_mode_desc")), 0, wx.EXPAND | wx.ALL, 4)
        self._mode_labels = [label for _, label in theme_mod.mode_choices()]
        self._mode_keys = [key for key, _ in theme_mod.mode_choices()]
        self._mode = wx.Choice(panel, choices=self._mode_labels)
        self._mode.SetName(i18n.t("display_mode"))
        current = str(s.get("display_mode", "normal_light"))
        if current in self._mode_keys:
            self._mode.SetSelection(self._mode_keys.index(current))
        self._mode.Bind(wx.EVT_CHOICE, self._on_mode_preview)
        sizer.Add(self._mode, 0, wx.EXPAND | wx.ALL, 4)

        sizer.Add(W.body(panel, i18n.t("font_scale")), 0, wx.ALL, 2)
        self._font = wx.SpinCtrlDouble(panel, min=0.6, max=3.0, inc=0.05)
        self._font.SetValue(float(s.get("font_scale", 1.0)))
        self._font.SetName(i18n.t("font_scale"))
        sizer.Add(self._font, 0, wx.EXPAND | wx.ALL, 4)

        sizer.Add(W.body(panel, "حجم خلايا برايل"), 0, wx.ALL, 2)
        self._cell = wx.SpinCtrlDouble(panel, min=0.6, max=3.0, inc=0.05)
        self._cell.SetValue(float(s.get("braille_cell_scale", 1.0)))
        self._cell.SetName("حجم خلايا برايل")
        sizer.Add(self._cell, 0, wx.EXPAND | wx.ALL, 4)

        self._bold = wx.CheckBox(panel, label=i18n.t("bold_text"))
        self._bold.SetValue(bool(s.get("bold_text", False)))
        self._bold.SetName(i18n.t("bold_text"))
        sizer.Add(self._bold, 0, wx.ALL, 4)

        self._dot_numbers = wx.CheckBox(panel, label=i18n.t("show_dot_numbers"))
        self._dot_numbers.SetValue(bool(s.get("show_dot_numbers", True)))
        sizer.Add(self._dot_numbers, 0, wx.ALL, 4)

        self._reduce_motion = wx.CheckBox(panel, label=i18n.t("reduce_motion"))
        self._reduce_motion.SetValue(bool(s.get("reduce_motion", False)))
        sizer.Add(self._reduce_motion, 0, wx.ALL, 4)

        # ألوان مخصّصة ------------------------------------------------
        cpanel, csizer = W.card(self, self.content, "ألوان مخصّصة")
        self._custom_colors = wx.CheckBox(cpanel, label="تفعيل الألوان المخصّصة")
        self._custom_colors.SetValue(bool(s.get("text_color") or s.get("background_color")))
        csizer.Add(self._custom_colors, 0, wx.ALL, 4)
        self._text_color = self._add_color_row(cpanel, csizer, "لون النص", s.get("text_color", "") or self.theme.colors["text"])
        self._bg_color = self._add_color_row(cpanel, csizer, "لون الخلفية", s.get("background_color", "") or self.theme.colors["background"])
        self._dot_on = self._add_color_row(cpanel, csizer, "لون النقاط المحدّدة", s.get("dot_color", "") or self.theme.colors["dot_on"])
        self._dot_off = self._add_color_row(cpanel, csizer, "لون النقاط غير المحدّدة", s.get("dot_empty_color", "") or self.theme.colors["dot_off"])

        # الصوت والنطق ------------------------------------------------
        spanel, ssizer = W.card(self, self.content, "الصوت والنطق")
        self._sound = wx.CheckBox(spanel, label="تشغيل الأصوات")
        self._sound.SetValue(bool(s.get("sound_enabled", True)))
        ssizer.Add(self._sound, 0, wx.ALL, 4)
        self._speech = wx.CheckBox(spanel, label="تشغيل النطق")
        self._speech.SetValue(bool(s.get("speech_enabled", False)))
        ssizer.Add(self._speech, 0, wx.ALL, 4)
        self._guidance = wx.CheckBox(spanel, label="الإرشادات الصوتية")
        self._guidance.SetValue(bool(s.get("guidance_enabled", True)))
        ssizer.Add(self._guidance, 0, wx.ALL, 4)
        ssizer.Add(W.body(spanel, "مستوى الصوت"), 0, wx.ALL, 2)
        self._volume = wx.SpinCtrlDouble(spanel, min=0.0, max=1.0, inc=0.05)
        self._volume.SetValue(float(s.get("volume", 1.0)))
        ssizer.Add(self._volume, 0, wx.EXPAND | wx.ALL, 4)
        ssizer.Add(W.body(spanel, "سرعة النطق"), 0, wx.ALL, 2)
        self._rate = wx.SpinCtrlDouble(spanel, min=-1.0, max=1.0, inc=0.05)
        self._rate.SetValue(float(s.get("speech_rate", 0.0)))
        ssizer.Add(self._rate, 0, wx.EXPAND | wx.ALL, 4)
        ssizer.Add(W.wrapped_text(spanel, f"{i18n.t('speech_status')}: {self.context.speech_status()}"), 0, wx.EXPAND | wx.ALL, 4)

        # اللغة والتعلّم ----------------------------------------------
        lpanel, lsizer = W.card(self, self.content, "اللغة والتعلّم")
        lsizer.Add(W.body(lpanel, i18n.t("ui_language")), 0, wx.ALL, 2)
        self._language = wx.Choice(lpanel, choices=[i18n.t("language_ar"), i18n.t("language_en")])
        self._language.SetSelection(1 if str(s.get("interface_language", "ar")) == "en" else 0)
        lsizer.Add(self._language, 0, wx.EXPAND | wx.ALL, 4)
        self._guided = wx.CheckBox(lpanel, label=i18n.t("guided_mode"))
        self._guided.SetValue(bool(s.get("guided_mode", True)))
        lsizer.Add(self._guided, 0, wx.ALL, 4)
        self._large_target = wx.CheckBox(lpanel, label=i18n.t("show_large_target"))
        self._large_target.SetValue(bool(s.get("show_large_target", True)))
        lsizer.Add(self._large_target, 0, wx.ALL, 4)
        lsizer.Add(W.body(lpanel, i18n.t("mastery_threshold")), 0, wx.ALL, 2)
        self._mastery = wx.SpinCtrlDouble(lpanel, min=0.0, max=100.0, inc=0.5)
        self._mastery.SetValue(float(s.get("mastery_threshold", 85.0)))
        lsizer.Add(self._mastery, 0, wx.EXPAND | wx.ALL, 4)

        # الأزرار ------------------------------------------------------
        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(W.action_button(self, i18n.t("save_settings"), primary=True, on_click=self._apply, tooltip="Ctrl+Enter"), 0, wx.RIGHT, 8)
        buttons.Add(W.action_button(self, i18n.t("reset_defaults"), on_click=self._reset), 0)
        self.content.Add(buttons, 0, wx.ALL, 8)

        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _add_color_row(self, parent: wx.Window, sizer: wx.Sizer, label: str, initial: str) -> wx.ColourPickerCtrl:
        sizer.Add(W.body(parent, label), 0, wx.ALL, 2)
        picker = wx.ColourPickerCtrl(parent, colour=theme_mod.to_colour(initial))
        picker.SetName(label)
        sizer.Add(picker, 0, wx.EXPAND | wx.ALL, 4)
        return picker

    def _on_mode_preview(self, event) -> None:
        if self._building:
            return
        index = self._mode.GetSelection()
        if index < 0:
            return
        self.context.settings.set("display_mode", self._mode_keys[index])
        wx.CallAfter(self.frame.apply_theme, True)

    def focus_edit_box(self) -> bool:
        self._mode.SetFocus()
        return True

    def _apply(self) -> None:
        s = self.context.settings
        index = self._mode.GetSelection()
        if index >= 0:
            s.set("display_mode", self._mode_keys[index])
        s.set("font_scale", float(self._font.GetValue()))
        s.set("braille_cell_scale", float(self._cell.GetValue()))
        s.set("bold_text", self._bold.GetValue())
        s.set("show_dot_numbers", self._dot_numbers.GetValue())
        s.set("reduce_motion", self._reduce_motion.GetValue())
        if self._custom_colors.GetValue():
            s.set("text_color", self._text_color.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
            s.set("background_color", self._bg_color.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
            s.set("dot_color", self._dot_on.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
            s.set("dot_empty_color", self._dot_off.GetColour().GetAsString(wx.C2S_HTML_SYNTAX))
        else:
            for key in ("text_color", "background_color", "dot_color", "dot_empty_color"):
                s.set(key, "")
        s.set("sound_enabled", self._sound.GetValue())
        s.set("speech_enabled", self._speech.GetValue())
        s.set("guidance_enabled", self._guidance.GetValue())
        s.set("volume", float(self._volume.GetValue()))
        s.set("speech_rate", float(self._rate.GetValue()))
        s.set("guided_mode", self._guided.GetValue())
        s.set("show_large_target", self._large_target.GetValue())
        s.set("mastery_threshold", float(self._mastery.GetValue()))
        language = "en" if self._language.GetSelection() == 1 else "ar"
        s.set("interface_language", language)

        self.context.apply_settings()
        self.frame.apply_theme(rebuild=True)
        if language != i18n.get_lang():
            i18n.set_lang(language)
            self.frame.rebuild_ui()
        else:
            self._rebuild_notice()
        self.frame.refresh_status()
        W.informational(self, i18n.t("settings"), i18n.t("save_settings_ok"))

    def _rebuild_notice(self) -> None:
        self._build()

    def confirm_action(self) -> bool:
        self._apply()
        return True

    def _reset(self) -> None:
        if W.confirm(self, i18n.t("reset_defaults"), "هل تريد إعادة جميع الإعدادات إلى القيم الافتراضية؟"):
            self.context.reset_settings()
            self.frame.apply_theme(rebuild=True)
            self._build()


# ----------------------------------------------------------------------
# وضع المدرب
# ----------------------------------------------------------------------
class InstructorPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("instructor"), self.theme), 0, wx.ALL, 8)

        panel, sizer = W.card(self, self.content, i18n.t("add_user"))
        self._name = W.editable_box(panel, name=i18n.t("user_name"), on_enter=self._add_user)
        sizer.Add(self._name, 0, wx.EXPAND | wx.ALL, 4)
        sizer.Add(W.action_button(panel, i18n.t("add_user"), on_click=self._add_user), 0, wx.ALL, 4)

        self._users = self._load_users()
        list_panel, list_sizer = W.card(self, self.content, i18n.t("students_list"))
        if not self._users:
            list_sizer.Add(W.body(list_panel, i18n.t("no_students")), 0, wx.ALL, 4)
        else:
            stats = self.context.progress.statistics()
            for user in self._users:
                row = W.body(
                    list_panel,
                    f"{user.name} ({i18n.t('teacher') if user.role == 'teacher' else i18n.t('student')}) — "
                    f"{i18n.t('accuracy')}: {int(stats['accuracy'])}% — "
                    f"{i18n.t('completed_lessons')}: {stats['lessons_completed']}",
                )
                list_sizer.Add(row, 0, wx.EXPAND | wx.ALL, 3)

        banner, bsizer = W.card(self, self.content, "تقرير الفصل")
        bsizer.Add(W.action_button(banner, i18n.t("export_csv"), on_click=self._export_csv), 0, wx.ALL, 4)
        self.content.AddStretchSpacer(1)
        self.finish_layout()

    def _load_users(self):
        try:
            from braille_go.data.users import UserManager

            return UserManager(self.context.database).list_users()
        except Exception:
            return []

    def _add_user(self) -> None:
        name = self._name.GetValue().strip() if self._name is not None else ""
        if not name:
            W.informational(self, i18n.t("add_user"), "أدخل الاسم أولًا.")
            return
        try:
            from braille_go.data.users import UserManager

            UserManager(self.context.database).add_user(name)
        except Exception as exc:
            W.informational(self, i18n.t("add_user"), f"تعذّر إضافة المستخدم: {exc}")
        self.activate()

    def _export_csv(self) -> None:
        default = f"braille_go_class_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with wx.FileDialog(self, i18n.t("export_csv"), wildcard="CSV (*.csv)|*.csv",
                           defaultFile=default, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dialog:
            if dialog.ShowModal() != wx.ID_OK:
                return
            path = dialog.GetPath()
        stats = self.context.progress.statistics()
        users = self._load_users()
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Student", "Role", "Accuracy%", "CompletedLessons"])
                for user in users:
                    writer.writerow([user.name, user.role, int(stats["accuracy"]), stats["lessons_completed"]])
            W.informational(self, i18n.t("export_csv"), f"تم التصدير إلى:\n{path}")
        except Exception as exc:
            W.informational(self, i18n.t("export_csv"), f"تعذّر التصدير: {exc}")

    def focus_edit_box(self) -> bool:
        if self._name is not None:
            self._name.SetFocus()
            return True
        return False


# ----------------------------------------------------------------------
# المساعدة
# ----------------------------------------------------------------------
class HelpPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("help"), self.theme), 0, wx.ALL, 8)

        about, asizer = W.card(self, self.content, i18n.t("what_is_braille_go"))
        asizer.Add(W.wrapped_text(about, i18n.t("braille_go_desc")), 0, wx.EXPAND | wx.ALL, 4)
        asizer.Add(W.wrapped_text(about, i18n.t("who_for") + ": " + i18n.t("who_for_desc")), 0, wx.EXPAND | wx.ALL, 4)
        asizer.Add(W.wrapped_text(about, i18n.t("importance") + ": " + i18n.t("importance_desc")), 0, wx.EXPAND | wx.ALL, 4)

        start, ssizer = W.card(self, self.content, "كيف تبدأ")
        ssizer.Add(W.wrapped_text(
            start,
            "1. ابدأ من الدروس والمستويات ثم اختر أول درس.\n"
            "2. اقرأ نص السؤال داخل صندوق الكتابة (يمكنك الرجوع إليه بـ Ctrl+E).\n"
            "3. أجِب: اختر خيارًا، أو اكتب في حقل الإجابة، أو حدّد النقاط بالأرقام 1-6.\n"
            "4. اضغط Ctrl+Enter للتأكيد، ثم Ctrl+N للسؤال التالي.\n"
            "5. يُفتح المستوى التالي بعد تحقيق نسبة الإتقان المطلوبة.",
        ), 0, wx.EXPAND | wx.ALL, 4)

        access, access_sizer = W.card(self, self.content, "إمكانية الوصول وقارئات الشاشة")
        access_sizer.Add(W.wrapped_text(
            access,
            "التطبيق مبني على عناصر wxPython الأصلية في Windows ليقرأها NVDA وWindows Narrator "
            "بشكل موثوق. نص السؤال داخل صندوق كتابة قابل للتركيز بالكامل، وكل زر له اسم واضح. "
            "وإذا لم يتوفّر صوت عربي يبقى التطبيق قابلًا للاستخدام بالكامل.",
        ), 0, wx.EXPAND | wx.ALL, 4)

        self.content.AddStretchSpacer(1)
        self.finish_layout()


# ----------------------------------------------------------------------
# الاختصارات
# ----------------------------------------------------------------------
#: (الاختصار، الوصف) لعرضها في شاشة الاختصارات وفي القوائم.
SHORTCUTS: tuple[tuple[str, str], ...] = (
    ("Ctrl+E", "الانتقال إلى مربع السؤال/الإجابة"),
    ("Ctrl+Enter / Enter", "تأكيد الإجابة"),
    ("Ctrl+N", "السؤال التالي"),
    ("Ctrl+R", "إعادة النطق"),
    ("Ctrl+1 … Ctrl+6", "تبديل النقطة 1 إلى 6 داخل خلية برايل"),
    ("Ctrl+Delete", "مسح النقاط/الإجابة"),
    ("Ctrl+B", "نص عريض"),
    ("Ctrl+Shift+D", "إظهار/إخفاء أرقام النقاط"),
    ("Ctrl+Shift+M", "تبديل نمط العرض"),
    ("Ctrl+= / Ctrl+-", "تكبير/تصغير الخط"),
    ("Ctrl+H", "الشاشة الرئيسية"),
    ("Ctrl+L", "الدروس والمستويات"),
    ("Ctrl+T", "التدريب"),
    ("Ctrl+X", "الاختبارات"),
    ("Ctrl+W", "مراجعة الأخطاء"),
    ("Ctrl+P", "متابعة التقدّم"),
    ("Ctrl+I", "وضع المدرب"),
    ("Ctrl+,", "الإعدادات"),
    ("F1", "المساعدة"),
    ("Shift+F1", "قائمة الاختصارات"),
    ("Alt+1 … Alt+9", "الانتقال السريع بين الشاشات"),
    ("Ctrl+Q", "خروج"),
)


class ShortcutsPanel(BasePanel):
    def activate(self, **kwargs) -> None:
        clear_sizer(self.content)
        self.content.Add(W.heading(self, i18n.t("shortcuts"), self.theme), 0, wx.ALL, 8)
        self.content.Add(W.wrapped_text(self, i18n.t("shortcuts_hint")), 0, wx.EXPAND | wx.ALL, 8)

        panel, sizer = W.card(self, self.content, i18n.t("shortcuts"))
        table = wx.ListCtrl(panel, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        table.InsertColumn(0, "الاختصار", width=200)
        table.InsertColumn(1, "الوظيفة", width=420)
        for index, (keys, description) in enumerate(SHORTCUTS):
            table.InsertItem(index, keys)
            table.SetItem(index, 1, description)
        table.SetName("جدول اختصارات لوحة المفاتيح")
        sizer.Add(table, 1, wx.EXPAND | wx.ALL, 4)
        self.content.AddStretchSpacer(1)
        self.finish_layout()
