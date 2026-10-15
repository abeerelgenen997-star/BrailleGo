"""النافذة الرئيسية لنسخة wxPython: القوائم والاختصارات وتوجيه الشاشات.

كل وظيفة في التطبيق لها اختصار لوحة مفاتيح (عبر القوائم وجدول الاختصارات)،
وأهم اختصار هو **Ctrl+E** للانتقال إلى مربع السؤال/الإجابة. تُستخدم عناصر
Windows الأصلية حتى يقرأها NVDA وWindows Narrator بموثوقية.
"""

from __future__ import annotations

import wx

from . import i18n
from . import theme as theme_mod
from .context import WxAppContext
from .lesson_view import LessonPanel
from .screens import (
    ExamsPanel,
    HelpPanel,
    HomePanel,
    InstructorPanel,
    LessonsPanel,
    PracticePanel,
    ProgressPanel,
    ReviewPanel,
    SettingsPanel,
    ShortcutsPanel,
    WelcomePanel,
)


class MainFrame(wx.Frame):
    """الإطار الرئيسي الذي يحتوي كل الشاشات."""

    def __init__(self, context: WxAppContext) -> None:
        super().__init__(None, title="Braille Go", size=(1120, 800))
        self.SetMinSize((760, 560))
        self.SetName("Braille Go")
        self.context = context
        self.theme = theme_mod.Theme(context.settings)
        i18n.set_lang(str(context.settings.get("interface_language", "ar")) or "ar")

        # مُعرّفات الأوامر.
        self.ID_FOCUS_QUESTION = wx.NewIdRef()
        self.ID_CONFIRM = wx.NewIdRef()
        self.ID_NEXT = wx.NewIdRef()
        self.ID_CLEAR = wx.NewIdRef()
        self.ID_REPEAT = wx.NewIdRef()
        self.ID_DOT = [wx.NewIdRef() for _ in range(6)]
        self.ID_NAV: dict[str, wx.WindowIDRef] = {}
        self.ID_NAV_ALT = [wx.NewIdRef() for _ in range(9)]
        self.ID_MODE: list[wx.WindowIDRef] = []
        self.ID_FONT_INC = wx.NewIdRef()
        self.ID_FONT_DEC = wx.NewIdRef()
        self.ID_TOGGLE_BOLD = wx.NewIdRef()
        self.ID_TOGGLE_DOTS = wx.NewIdRef()
        self.ID_TOGGLE_MODE = wx.NewIdRef()
        self.ID_ABOUT = wx.NewIdRef()

        self._current_id = ""
        self._panels: dict[str, object] = {}

        self.CreateStatusBar(2)
        self.GetStatusBar().SetStatusWidths([-1, 320])

        self._container = wx.Panel(self)
        self._container_sizer = wx.BoxSizer(wx.VERTICAL)
        self._container.SetSizer(self._container_sizer)

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(self._container, 1, wx.EXPAND)
        self.SetSizer(root)

        self._build_panels()
        self._build_menu()
        self._build_accelerators()
        self._bind_events()

        self.apply_theme()
        self.refresh_status()

        if not self.context.settings.get("welcome_shown", False):
            self.navigate_to("welcome")
        else:
            self.navigate_to("home")
        wx.CallAfter(self._focus_current)

    # ------------------------------------------------------------------
    # البناء
    # ------------------------------------------------------------------
    def _build_panels(self) -> None:
        self._panels = {}
        classes = {
            "welcome": WelcomePanel,
            "home": HomePanel,
            "lessons": LessonsPanel,
            "lesson": LessonPanel,
            "practice": PracticePanel,
            "exams": ExamsPanel,
            "review": ReviewPanel,
            "progress": ProgressPanel,
            "settings": SettingsPanel,
            "instructor": InstructorPanel,
            "help": HelpPanel,
            "shortcuts": ShortcutsPanel,
        }
        for screen_id, panel_class in classes.items():
            panel = panel_class(self._container, self.context, self)
            panel.Hide()
            self._container_sizer.Add(panel, 1, wx.EXPAND)
            self._panels[screen_id] = panel

    def _build_menu(self) -> None:
        bar = wx.MenuBar()

        file_menu = wx.Menu()
        item = file_menu.Append(wx.ID_ANY, i18n.t("settings") + "\tCtrl+,", i18n.t("settings"))
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("settings"), item)
        file_menu.AppendSeparator()
        item = file_menu.Append(wx.ID_EXIT, i18n.t("quit") + "\tCtrl+Q", i18n.t("quit"))
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), item)
        bar.Append(file_menu, i18n.t("menu_file"))

        learn_menu = wx.Menu()
        learn_items = [
            ("home", i18n.t("app_name"), "Ctrl+H"),
            ("lessons", i18n.t("lessons_levels"), "Ctrl+L"),
            ("practice", i18n.t("practice"), "Ctrl+T"),
            ("exams", i18n.t("exams"), "Ctrl+X"),
            ("review", i18n.t("review_errors"), "Ctrl+W"),
            ("progress", i18n.t("progress"), "Ctrl+P"),
            ("instructor", i18n.t("instructor"), "Ctrl+I"),
        ]
        for screen_id, label, accel in learn_items:
            item = learn_menu.Append(wx.ID_ANY, f"{label}\t{accel}", label)
            self.ID_NAV[screen_id] = item.GetId()
            self.Bind(wx.EVT_MENU, lambda event, sid=screen_id: self.navigate_to(sid), item)
        bar.Append(learn_menu, i18n.t("menu_learn"))

        view_menu = wx.Menu()
        self.ID_MODE = []
        for index, (key, label) in enumerate(theme_mod.mode_choices()):
            item = view_menu.AppendRadioItem(wx.ID_ANY, label, i18n.t("display_mode"))
            self.ID_MODE.append(item.GetId())
            if key == str(self.context.settings.get("display_mode", "normal_light")):
                item.Check(True)
            self.Bind(wx.EVT_MENU, lambda event, k=key: self._set_mode(k), item)
        view_menu.AppendSeparator()
        self._font_inc_item = view_menu.Append(wx.ID_ANY, "تكبير الخط\tCtrl+=", "تكبير الخط")
        self.Bind(wx.EVT_MENU, lambda event: self._change_font(0.1), self._font_inc_item)
        self._font_dec_item = view_menu.Append(wx.ID_ANY, "تصغير الخط\tCtrl+-", "تصغير الخط")
        self.Bind(wx.EVT_MENU, lambda event: self._change_font(-0.1), self._font_dec_item)
        self._bold_item = view_menu.AppendCheckItem(wx.ID_ANY, i18n.t("bold_text"))
        self._bold_item.Check(bool(self.context.settings.get("bold_text", False)))
        self.Bind(wx.EVT_MENU, lambda event: self._toggle_setting("bold_text"), self._bold_item)
        self._dots_item = view_menu.AppendCheckItem(wx.ID_ANY, i18n.t("show_dot_numbers"))
        self._dots_item.Check(bool(self.context.settings.get("show_dot_numbers", True)))
        self.Bind(wx.EVT_MENU, lambda event: self._toggle_setting("show_dot_numbers"), self._dots_item)
        bar.Append(view_menu, i18n.t("menu_view"))

        help_menu = wx.Menu()
        item = help_menu.Append(wx.ID_ANY, i18n.t("help") + "\tF1", i18n.t("help"))
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("help"), item)
        item = help_menu.Append(wx.ID_ANY, i18n.t("shortcuts") + "\tShift+F1", i18n.t("shortcuts"))
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("shortcuts"), item)
        help_menu.AppendSeparator()
        item = help_menu.Append(wx.ID_ABOUT, "عن البرنامج", "عن البرنامج")
        self.Bind(wx.EVT_MENU, self._on_about, item)
        bar.Append(help_menu, i18n.t("menu_help"))

        old = self.GetMenuBar()
        self.SetMenuBar(bar)
        if old is not None:
            old.Destroy()

    #: ترتيب الشاشات لمفتاح التنقّل السريع Alt+1..9.
    ALT_SCREENS = (
        "home",
        "lessons",
        "practice",
        "exams",
        "review",
        "progress",
        "instructor",
        "settings",
        "help",
    )

    def _build_accelerators(self) -> None:
        e = wx.AcceleratorEntry
        entries = [
            e(wx.ACCEL_CTRL, ord("E"), self.ID_FOCUS_QUESTION),
            e(wx.ACCEL_CTRL, wx.WXK_RETURN, self.ID_CONFIRM),
            e(wx.ACCEL_CTRL, ord("N"), self.ID_NEXT),
            e(wx.ACCEL_CTRL, ord("R"), self.ID_REPEAT),
            e(wx.ACCEL_CTRL, wx.WXK_DELETE, self.ID_CLEAR),
            e(wx.ACCEL_CTRL, ord("B"), self.ID_TOGGLE_BOLD),
            e(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("D"), self.ID_TOGGLE_DOTS),
            e(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord("M"), self.ID_TOGGLE_MODE),
            e(wx.ACCEL_CTRL, ord("="), self.ID_FONT_INC),
            e(wx.ACCEL_CTRL, ord("+"), self.ID_FONT_INC),
            e(wx.ACCEL_CTRL, ord("-"), self.ID_FONT_DEC),
        ]
        for index in range(6):
            entries.append(e(wx.ACCEL_CTRL, ord("1") + index, self.ID_DOT[index]))
        for index in range(9):
            entries.append(e(wx.ACCEL_ALT, ord("1") + index, self.ID_NAV_ALT[index]))
        table = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(table)

    def _bind_events(self) -> None:
        self.Bind(wx.EVT_MENU, self._on_focus_question, id=self.ID_FOCUS_QUESTION)
        self.Bind(wx.EVT_MENU, self._on_confirm, id=self.ID_CONFIRM)
        self.Bind(wx.EVT_MENU, self._on_next, id=self.ID_NEXT)
        self.Bind(wx.EVT_MENU, self._on_clear, id=self.ID_CLEAR)
        self.Bind(wx.EVT_MENU, self._on_repeat, id=self.ID_REPEAT)
        self.Bind(wx.EVT_MENU, self._on_toggle_bold, id=self.ID_TOGGLE_BOLD)
        self.Bind(wx.EVT_MENU, self._on_toggle_dots, id=self.ID_TOGGLE_DOTS)
        self.Bind(wx.EVT_MENU, self._on_toggle_mode, id=self.ID_TOGGLE_MODE)
        self.Bind(wx.EVT_MENU, lambda event: self._change_font(0.1), id=self.ID_FONT_INC)
        self.Bind(wx.EVT_MENU, lambda event: self._change_font(-0.1), id=self.ID_FONT_DEC)
        for index in range(6):
            self.Bind(wx.EVT_MENU, lambda event, d=index + 1: self._on_dot(d), id=self.ID_DOT[index])
        for index in range(9):
            self.Bind(
                wx.EVT_MENU,
                lambda event, sid=self.ALT_SCREENS[index]: self.navigate_to(sid),
                id=self.ID_NAV_ALT[index],
            )
        self.Bind(wx.EVT_CLOSE, self._on_close)

    # ------------------------------------------------------------------
    # التنقّل
    # ------------------------------------------------------------------
    def navigate_to(self, screen_id: str, **kwargs) -> None:
        panel = self._panels.get(screen_id)
        if panel is None:
            return
        previous = self._panels.get(self._current_id)
        if previous is not None and previous is not panel:
            deactivate = getattr(previous, "deactivate", None)
            if callable(deactivate):
                try:
                    deactivate()
                except Exception:
                    pass
        for other in self._panels.values():
            other.Hide()
        panel.Show()
        self._current_id = screen_id
        self._container.Layout()
        activate = getattr(panel, "activate", None)
        if callable(activate):
            activate(**kwargs)
        self.refresh_status()
        wx.CallAfter(self._focus_current)

    def _focus_current(self) -> None:
        panel = self._panels.get(self._current_id)
        if panel is None:
            return
        focus = getattr(panel, "focus_default", None)
        if callable(focus) and focus():
            return
        try:
            panel.SetFocus()
        except Exception:
            pass

    @property
    def current_panel(self):
        return self._panels.get(self._current_id)

    # ------------------------------------------------------------------
    # أوامر الشاشة الحالية
    # ------------------------------------------------------------------
    def _on_focus_question(self, event) -> None:
        panel = self.current_panel
        method = getattr(panel, "focus_edit_box", None)
        if callable(method):
            method()

    def _on_confirm(self, event) -> None:
        panel = self.current_panel
        method = getattr(panel, "confirm_action", None)
        if callable(method):
            method()

    def _on_next(self, event) -> None:
        panel = self.current_panel
        method = getattr(panel, "next_action", None)
        if callable(method):
            method()

    def _on_clear(self, event) -> None:
        self._dispatch_shortcut("clear")

    def _on_repeat(self, event) -> None:
        self._dispatch_shortcut("repeat")

    def _on_dot(self, dot: int) -> None:
        self._dispatch_shortcut(f"dot{dot}")

    def _dispatch_shortcut(self, key: str) -> None:
        panel = self.current_panel
        method = getattr(panel, "on_shortcut", None)
        if callable(method):
            method(key)

    # ------------------------------------------------------------------
    # المظهر
    # ------------------------------------------------------------------
    def apply_theme(self, rebuild: bool = False) -> None:
        self.theme.refresh()
        theme_mod.apply_theme_to(self, self.theme)
        for panel in self._panels.values():
            handler = getattr(panel, "on_theme_changed", None)
            if callable(handler):
                try:
                    handler()
                except Exception:
                    pass
        try:
            self.Layout()
            self._container.Layout()
        except Exception:
            pass

    def _set_mode(self, key: str) -> None:
        self.context.settings.set("display_mode", key)
        self._sync_menu_checks()
        self.apply_theme(rebuild=True)

    def _change_font(self, delta: float) -> None:
        try:
            current = float(self.context.settings.get("font_scale", 1.0))
        except (TypeError, ValueError):
            current = 1.0
        self.context.settings.set("font_scale", round(max(0.6, min(3.0, current + delta)), 2))
        self.apply_theme(rebuild=True)

    def _toggle_setting(self, key: str) -> None:
        value = not bool(self.context.settings.get(key, False))
        self.context.settings.set(key, value)
        self._sync_menu_checks()
        self.apply_theme(rebuild=True)

    def _on_toggle_bold(self, event) -> None:
        self._toggle_setting("bold_text")

    def _on_toggle_dots(self, event) -> None:
        self._toggle_setting("show_dot_numbers")

    def _on_toggle_mode(self, event) -> None:
        keys = [key for key, _ in theme_mod.mode_choices()]
        if not keys:
            return
        current = str(self.context.settings.get("display_mode", keys[0]))
        try:
            index = keys.index(current)
        except ValueError:
            index = -1
        self._set_mode(keys[(index + 1) % len(keys)])

    def _sync_menu_checks(self) -> None:
        """مزامنة علامات الصحّ في القائمة مع الإعدادات الحالية."""
        try:
            if getattr(self, "_bold_item", None) is not None:
                self._bold_item.Check(bool(self.context.settings.get("bold_text", False)))
            if getattr(self, "_dots_item", None) is not None:
                self._dots_item.Check(bool(self.context.settings.get("show_dot_numbers", True)))
            template = "normal_light"
            if hasattr(theme_mod, "DEFAULT_MODE"):
                template = getattr(theme_mod, "DEFAULT_MODE")
            current = str(self.context.settings.get("display_mode", template))
            choices = [key for key, _ in theme_mod.mode_choices()]
            for item_id, key in zip(self.ID_MODE, choices):
                try:
                    bar = self.GetMenuBar()
                    if bar is not None:
                        bar.Check(item_id, key == current)
                except Exception:
                    pass
        except Exception:
            pass

    def rebuild_ui(self) -> None:
        """أعِد بناء الواجهة (يُستخدم عند تغيير اللغة)."""
        self._container_sizer.Clear(True)
        self._panels = {}
        self._build_panels()
        self._build_menu()
        self._build_accelerators()
        self.apply_theme()
        self.navigate_to("home")

    # ------------------------------------------------------------------
    def refresh_status(self) -> None:
        try:
            stats = self.context.progress.statistics()
            accuracy = int(round(float(stats.get("accuracy", 0.0))))
            progress = int(round(self.context.overall_progress_percent()))
            left = f"التقدّم العام {progress}% — الدقة {accuracy}%"
        except Exception:
            left = ""
        right = self.context.speech_status()
        bar = self.GetStatusBar()
        if bar is not None:
            bar.SetStatusText(left, 0)
            bar.SetStatusText(right, 1)

    def _on_about(self, event) -> None:
        text = (
            "Braille Go — تطبيق تعليمي تفاعلي لتعلّم طريقة برايل.\n"
            "واجهة wxPython أصلية لدعم أفضل لقارئات الشاشة.\n"
            "يعمل دون اتصال بالإنترنت ويحفظ التقدّم محليًا."
        )
        wx.MessageBox(text, "عن البرنامج", wx.OK | wx.ICON_INFORMATION, self)

    def _on_close(self, event) -> None:
        try:
            self.context.shutdown()
        except Exception:
            pass
        event.Skip()
