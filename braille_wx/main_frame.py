"""النافذة الرئيسية لنسخة wxPython: القوائم والاختصارات وتوجيه الشاشات.

كل وظيفة في التطبيق لها اختصار لوحة مفاتيح (عبر القوائم وجدول الاختصارات)،
وأهم اختصار هو **Ctrl+E** للانتقال إلى مربع السؤال/الإجابة. تُستخدم عناصر
Windows الأصلية حتى يقرأها NVDA وWindows Narrator بموثوقية.
"""

from __future__ import annotations

import wx

from braille_go.core.curriculum import LEVELS

from . import i18n
from . import theme as theme_mod
from . import widgets as W
from .context import WxAppContext
from .lesson_view import LessonPanel
from .screens import (
    AlphabetPanel,
    ExamsPanel,
    HelpPanel,
    HomePanel,
    InstructorPanel,
    LessonsPanel,
    MatchPanel,
    PlacementPanel,
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
        self._current_kwargs: dict = {}
        self._history: list[tuple[str, dict]] = []
        self._panels: dict[str, object] = {}

        self.CreateStatusBar(2)
        self.GetStatusBar().SetStatusWidths([-1, 320])

        self._container = wx.Panel(self)
        self._container_sizer = wx.BoxSizer(wx.VERTICAL)
        self._container.SetSizer(self._container_sizer)

        self._root_sizer = wx.BoxSizer(wx.VERTICAL)
        self._root_sizer.Add(self._container, 1, wx.EXPAND)
        self._build_navbar()
        self.SetSizer(self._root_sizer)

        self._build_panels()
        self._build_menu()
        self._build_accelerators()
        self._bind_events()
        self._apply_layout_direction()

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
            "alphabet": AlphabetPanel,
            "lesson": LessonPanel,
            "practice": PracticePanel,
            "placement": PlacementPanel,
            "match": MatchPanel,
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

    def _build_navbar(self) -> None:
        """شريط تنقّل قياسي أسفل النافذة: رجوع / الرئيسية / خروج.

        يمنح المستخدم أزرارًا مألوفة كما في برامج ويندوز، ويعمل مع مفتاح Esc
        (رجوع) ومع مفتاح الإدخال (تشغيل الزر المُركَّز عليه).
        """
        self._navbar = wx.Panel(self)
        self._navbar.SetName(i18n.t("nav_bar"))
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_back = W.action_button(
            self._navbar, i18n.t("nav_back"),
            on_click=self.go_back, tooltip=i18n.t("nav_back_tip"),
        )
        self._btn_home = W.action_button(
            self._navbar, i18n.t("nav_home"),
            on_click=lambda: self.navigate_to("home"), tooltip=i18n.t("nav_home_tip"),
        )
        self._btn_exit = W.action_button(
            self._navbar, i18n.t("btn_exit"),
            on_click=self.Close, tooltip=i18n.t("btn_exit_tip"),
        )
        sizer.Add(self._btn_back, 0, wx.ALL, 6)
        sizer.Add(self._btn_home, 0, wx.ALL, 6)
        sizer.Add((0, 0), 1, wx.EXPAND)
        sizer.Add(self._btn_exit, 0, wx.ALL, 6)
        self._navbar.SetSizer(sizer)
        self._root_sizer.Add(self._navbar, 0, wx.EXPAND)

    def _update_navbar_labels(self) -> None:
        """حدّث نصوص شريط التنقّل بعد تغيير اللغة."""
        try:
            for button, key in (
                (self._btn_back, "nav_back"),
                (self._btn_home, "nav_home"),
                (self._btn_exit, "btn_exit"),
            ):
                button.SetLabel(i18n.t(key))
                button.SetName(i18n.t(key))
            self._navbar.SetName(i18n.t("nav_bar"))
            self._navbar.Layout()
        except Exception:
            pass

    def _build_menu(self) -> None:
        bar = wx.MenuBar()

        file_menu = wx.Menu()
        item = file_menu.Append(wx.ID_ANY, i18n.t("settings") + "\tCtrl+,", i18n.t("settings"))
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("settings"), item)
        file_menu.AppendSeparator()
        item = file_menu.Append(wx.ID_EXIT, i18n.t("quit") + "\tCtrl+Q", i18n.t("quit"))
        self.Bind(wx.EVT_MENU, lambda event: self.Close(), item)
        bar.Append(file_menu, i18n.t("menu_file"))

        # الدروس: قائمة منسدلة فيها كل الدروس مرتّبة حسب المستويات -----------
        lessons_menu = wx.Menu()
        item = lessons_menu.Append(wx.ID_ANY, i18n.t("all_lessons") + "\tCtrl+L", i18n.t("all_lessons"))
        self.ID_NAV["lessons"] = item.GetId()
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("lessons"), item)
        lessons_menu.AppendSeparator()
        for level in LEVELS:
            submenu = wx.Menu()
            for lesson in level.lessons:
                sub_item = submenu.Append(wx.ID_ANY, i18n.lesson_title(lesson), i18n.lesson_description(lesson))
                self.Bind(
                    wx.EVT_MENU,
                    lambda event, lk=lesson.key, lv=level.key: self.navigate_to("lesson", lesson_key=lk, level_key=lv),
                    sub_item,
                )
            lessons_menu.AppendSubMenu(submenu, f"{level.number}. {i18n.level_title(level)}")
        bar.Append(lessons_menu, i18n.t("menu_lessons"))

        # التدريبات --------------------------------------------------------
        practice_menu = wx.Menu()
        practice_items = [
            ("practice", i18n.t("general_practice"), "Ctrl+T"),
            ("review", i18n.t("review_errors"), "Ctrl+W"),
            ("match", i18n.t("match_title"), ""),
            ("alphabet", i18n.t("alphabet_guide"), "Ctrl+Shift+A"),
        ]
        for screen_id, label, accel in practice_items:
            text = f"{label}\t{accel}" if accel else label
            item = practice_menu.Append(wx.ID_ANY, text, label)
            self.ID_NAV[screen_id] = item.GetId()
            self.Bind(wx.EVT_MENU, lambda event, sid=screen_id: self.navigate_to(sid), item)
        bar.Append(practice_menu, i18n.t("menu_practice"))

        # الاختبارات + تحديد المستوى --------------------------------------
        exams_menu = wx.Menu()
        item = exams_menu.Append(wx.ID_ANY, i18n.t("exams_levels_title") + "\tCtrl+X", i18n.t("exams_levels_title"))
        self.ID_NAV["exams"] = item.GetId()
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("exams"), item)
        exams_menu.AppendSeparator()
        item = exams_menu.Append(wx.ID_ANY, i18n.t("placement"), i18n.t("placement_desc"))
        self.ID_NAV["placement"] = item.GetId()
        self.Bind(wx.EVT_MENU, lambda event: self.navigate_to("placement"), item)
        bar.Append(exams_menu, i18n.t("menu_exams"))

        # الانتقال ---------------------------------------------------------
        go_menu = wx.Menu()
        go_items = [
            ("home", i18n.t("app_name"), "Ctrl+H"),
            ("progress", i18n.t("progress"), "Ctrl+P"),
            ("instructor", i18n.t("instructor"), "Ctrl+I"),
        ]
        for screen_id, label, accel in go_items:
            item = go_menu.Append(wx.ID_ANY, f"{label}\t{accel}", label)
            self.ID_NAV[screen_id] = item.GetId()
            self.Bind(wx.EVT_MENU, lambda event, sid=screen_id: self.navigate_to(sid), item)
        bar.Append(go_menu, i18n.t("menu_go"))

        view_menu = wx.Menu()
        self.ID_MODE = []
        for index, (key, label) in enumerate(theme_mod.mode_choices()):
            item = view_menu.AppendRadioItem(wx.ID_ANY, label, i18n.t("display_mode"))
            self.ID_MODE.append(item.GetId())
            if key == str(self.context.settings.get("display_mode", "normal_light")):
                item.Check(True)
            self.Bind(wx.EVT_MENU, lambda event, k=key: self._set_mode(k), item)
        view_menu.AppendSeparator()
        self._font_inc_item = view_menu.Append(wx.ID_ANY, i18n.t("zoom_in") + "\tCtrl+=", i18n.t("zoom_in"))
        self.Bind(wx.EVT_MENU, lambda event: self._change_font(0.1), self._font_inc_item)
        self._font_dec_item = view_menu.Append(wx.ID_ANY, i18n.t("zoom_out") + "\tCtrl+-", i18n.t("zoom_out"))
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
        item = help_menu.Append(wx.ID_ABOUT, i18n.t("about_program"), i18n.t("about_program"))
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
        # مفتاح الإدخال (Enter) للتأكيد والانتقال — على مستوى الإطار ليعمل مع
        # مختلف عناصر الشاشة، تنفيذًا لتعليمات المراجعة (Enter بدل Ctrl+Enter).
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event) -> None:
        """اعتراض مفاتيح الإدخال (Enter) و«Esc» وتوجيهها إلى الشاشة الحالية."""
        code = event.GetKeyCode()
        control = getattr(event, "ControlDown", lambda: False)()
        alt = getattr(event, "AltDown", lambda: False)()
        if code == wx.WXK_ESCAPE and not control and not alt:
            # «Esc» = رجوع إلى الشاشة السابقة (سلوك مألوف في ويندوز).
            if self.go_back():
                return
            event.Skip()
            return
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and not control and not alt:
            # إن كان التركيز على زر (مثل أزرار شريط التنقّل أو أزرار الخيارات)
            # نترك ويندوز يتعامل مع مفتاح الإدخال طبيعيًا فيعمل الزر.
            focused = wx.Window.FindFocus()
            if isinstance(focused, wx.Button):
                event.Skip()
                return
            panel = self.current_panel
            method = getattr(panel, "on_enter", None)
            if callable(method):
                try:
                    if method():
                        return  # تمّت المعالجة، لا تُمرّر الحدث.
                except Exception:
                    pass
        event.Skip()

    # ------------------------------------------------------------------
    # التنقّل
    # ------------------------------------------------------------------
    def navigate_to(self, screen_id: str, _record: bool = True, **kwargs) -> None:
        panel = self._panels.get(screen_id)
        if panel is None:
            return
        if _record and self._current_id and self._current_id != screen_id:
            self._history.append((self._current_id, dict(self._current_kwargs)))
            if len(self._history) > 50:
                self._history.pop(0)
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
        self._current_kwargs = dict(kwargs)
        self._container.Layout()
        activate = getattr(panel, "activate", None)
        if callable(activate):
            activate(**kwargs)
        self.refresh_status()
        wx.CallAfter(self._focus_current)

    def go_back(self) -> bool:
        """العودة إلى الشاشة السابقة (زر «رجوع» أو مفتاح Esc).

        تُعيد ``True`` إن انتقلت فعلًا، و``False`` إن لم يوجد ما يعود إليه
        (فنبقى في الشاشة الحالية إن كانت الرئيسية).
        """
        while self._history:
            previous_id, previous_kwargs = self._history.pop()
            if previous_id in self._panels and previous_id != self._current_id:
                self.navigate_to(previous_id, _record=False, **previous_kwargs)
                return True
        if self._current_id != "home":
            self.navigate_to("home", _record=False)
            return True
        return False

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

    def _apply_layout_direction(self) -> None:
        """اضبط اتجاه التخطيط (يمين→يسار للعربية ويسار→يمين لغيرها).

        تُطبَّق على الإطار وكل عناصره الفرعية حتى تظهر القوائم والأزرار
        والحقول بالاتجاه الصحيح للّغة المختارة.
        """
        try:
            direction = (
                wx.Layout_RightToLeft if i18n.is_rtl() else wx.Layout_LeftToRight
            )
        except Exception:
            return

        def visit(win: wx.Window) -> None:
            try:
                win.SetLayoutDirection(direction)
            except Exception:
                pass
            for child in win.GetChildren():
                visit(child)

        visit(self)

    def rebuild_ui(self) -> None:
        """أعِد بناء الواجهة (يُستخدم عند تغيير اللغة)."""
        self._history = []
        self._container_sizer.Clear(True)
        self._panels = {}
        self._build_panels()
        self._build_menu()
        self._build_accelerators()
        self._update_navbar_labels()
        self._apply_layout_direction()
        self.apply_theme()
        self.navigate_to("home")

    # ------------------------------------------------------------------
    def refresh_status(self) -> None:
        try:
            stats = self.context.progress.statistics()
            accuracy = int(round(float(stats.get("accuracy", 0.0))))
            progress = int(round(self.context.overall_progress_percent()))
            left = i18n.t("status_progress").format(progress=progress, accuracy=accuracy)
        except Exception:
            left = ""
        right = self.context.speech_status()
        bar = self.GetStatusBar()
        if bar is not None:
            bar.SetStatusText(left, 0)
            bar.SetStatusText(right, 1)

    def _on_about(self, event) -> None:
        wx.MessageBox(i18n.t("about_text"), i18n.t("about_program"), wx.OK | wx.ICON_INFORMATION, self)

    def _on_close(self, event) -> None:
        try:
            self.context.shutdown()
        except Exception:
            pass
        event.Skip()
