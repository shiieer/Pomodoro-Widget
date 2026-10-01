"""
UI Smoke Tests — verify that all major widgets and windows can be
instantiated and show without crashing.

These tests run headless via QT_QPA_PLATFORM=offscreen and do NOT
interact with real display hardware.

Covers:
  - PomodoroApp (main window)
  - MiniWidget
  - SettingsWindow (all 3 pages)
  - TaskPanel (add, toggle, delete, clear via store)
  - TaskCard.setTask
  - ArcProgressRing.setState
  - SessionDots.setState
  - FooterStrip.setState
  - ToggleSwitch (settings/cards.py)
  - SectionCard / RowItem
"""

import os
import sys

import pytest

# Must be set BEFORE any Qt import
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.settings_store import SettingsStore
from core.task_store import TaskStore

# ── QApplication singleton ────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def qapp():
    """One QApplication for the whole test session."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


@pytest.fixture
def store(tmp_path):
    return SettingsStore(path=tmp_path / "settings.json")


@pytest.fixture
def task_store(tmp_path):
    return TaskStore(path=tmp_path / "tasks.json")


# ── PomodoroApp ───────────────────────────────────────────────────────────────


class TestPomodoroApp:
    def test_instantiation(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        assert w is not None
        w.close()

    def test_window_title(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        assert w.windowTitle() == "FocusTimer"
        w.close()

    def test_has_timer(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        from core.timer import PomodoroTimer

        assert isinstance(w.timer, PomodoroTimer)
        w.close()

    def test_task_card_shows_active_task(self, qapp, tmp_path):
        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        ts = TaskStore(path=tmp_path / "t.json")
        ts.add("My Focus Task")

        w = PomodoroApp(store)
        # patch the store and refresh
        w._task_store = ts
        w._refresh_task_card()
        assert "My Focus Task" in w.task_card._task_name
        w.close()

    def test_task_card_no_tasks_message(self, qapp, tmp_path):
        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        ts = TaskStore(path=tmp_path / "t.json")

        w = PomodoroApp(store)
        w._task_store = ts
        w._refresh_task_card()
        assert (
            "add" in w.task_card._task_name.lower()
            or "task" in w.task_card._task_name.lower()
        )
        w.close()

    def test_open_tasks_creates_panel(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        assert w._task_panel is None
        w.open_tasks()
        assert w._task_panel is not None
        w._task_panel.close()
        w.close()

    def test_open_tasks_twice_does_not_create_second_panel(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        w.open_tasks()
        panel1 = w._task_panel
        w.open_tasks()
        assert w._task_panel is panel1  # same object
        w._task_panel.close()
        w.close()

    def test_timer_tick_updates_arc(self, qapp, store):
        from core.timer import Phase
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        w._on_tick(600, Phase.WORK)
        assert w.arc._time_text == "10:00"
        w.close()

    def test_reset_stops_timer(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        w = PomodoroApp(store)
        w.timer.running = True
        w._reset()
        assert w.timer.running is False
        w.close()

    def test_apply_settings_updates_timer_durations(self, qapp, tmp_path):
        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        store.update({"work_minutes": 30})
        w = PomodoroApp(store)
        w.apply_settings()
        assert w.timer.work_seconds == 30 * 60
        w.close()


# ── MiniWidget ────────────────────────────────────────────────────────────────


class TestMiniWidget:
    def test_instantiation(self, qapp, store):
        from ui.app.app_window import PomodoroApp

        app_w = PomodoroApp(store)
        mini = app_w.mini_widget
        assert mini is not None
        app_w.close()

    def test_update_tick_changes_label(self, qapp, store):
        from core.timer import Phase
        from ui.app.app_window import PomodoroApp

        app_w = PomodoroApp(store)
        app_w.mini_widget.update_tick(300, Phase.WORK, 1500)
        assert app_w.mini_widget.time_label.text() == "05:00"
        app_w.close()

    def test_phase_labels(self, qapp, store):
        from core.timer import Phase
        from ui.app.app_window import PomodoroApp

        app_w = PomodoroApp(store)
        app_w.mini_widget.update_tick(0, Phase.SHORT_BREAK, 300)
        assert "BREAK" in app_w.mini_widget.phase_label.text().upper()
        app_w.close()


# ── SettingsWindow ────────────────────────────────────────────────────────────


class TestSettingsWindow:
    def test_instantiation(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        assert w is not None
        w.close()

    def test_page_count(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        assert w.pages.count() == 3
        w.close()

    def test_sidebar_row_count(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        assert w.sidebar.count() == 3
        w.close()

    def test_timer_values_has_required_keys(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        v = w.timer_card.values()
        for key in (
            "work_minutes",
            "short_break_minutes",
            "long_break_minutes",
            "sessions_until_long_break",
        ):
            assert key in v, f"Missing key: {key}"
        w.close()

    def test_look_values_has_required_keys(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        v = w.look_card.values()
        for key in (
            "corner",
            "margin",
            "opacity",
            "always_on_top",
            "timer_font_family",
            "timer_font_size",
        ):
            assert key in v, f"Missing key: {key}"
        w.close()

    def test_media_values_has_gifs_key(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        v = w.media_card.values()
        assert "gifs" in v
        assert "work" in v["gifs"]
        assert "short_break" in v["gifs"]
        assert "long_break" in v["gifs"]
        w.close()

    def test_values_aggregates_all_pages(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        v = w.values()
        assert "work_minutes" in v
        assert "corner" in v
        assert "gifs" in v
        w.close()

    def test_timer_card_reset(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        w.timer_card.work.setValue(99)
        w.timer_card.reset()
        assert w.timer_card.work.value() == DEFAULT_SETTINGS["work_minutes"]
        w.close()

    def test_look_card_reset(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        w.look_card.opacity.setValue(0.3)
        w.look_card.reset()
        assert abs(w.look_card.opacity.value() - DEFAULT_SETTINGS["opacity"]) < 0.01
        w.close()

    def test_toggle_switch_initial_state(self, qapp, store):
        from ui.settings import SettingsWindow

        w = SettingsWindow(store)
        # skip_toggle should match store value (default False)
        assert w.timer_card.skip_toggle.isChecked() is False
        w.close()

    def test_toggle_switch_toggle(self, qapp, store):
        from ui.settings.cards import ToggleSwitch

        ts = ToggleSwitch(False)
        assert ts.isChecked() is False
        ts.setChecked(True)
        assert ts.isChecked() is True
        ts.setChecked(False)
        assert ts.isChecked() is False


# ── TaskPanel ─────────────────────────────────────────────────────────────────


class TestTaskPanel:
    def test_instantiation(self, qapp, task_store):
        from ui.task import TaskPanel

        p = TaskPanel(task_store)
        assert p is not None
        p.close()

    def test_window_title(self, qapp, task_store):
        from ui.task import TaskPanel

        p = TaskPanel(task_store)
        assert p.windowTitle() == "Tasks"
        p.close()

    def test_add_task_via_input(self, qapp, task_store):
        from ui.task import TaskPanel

        p = TaskPanel(task_store)
        p._input.setText("Test task from UI")
        p._add_task()
        assert task_store.pending_count() == 1
        p.close()

    def test_add_empty_input_does_nothing(self, qapp, task_store):
        from ui.task import TaskPanel

        p = TaskPanel(task_store)
        p._input.setText("   ")
        p._add_task()
        assert task_store.pending_count() == 0
        p.close()

    def test_task_changed_signal_fires_on_add(self, qapp, task_store):
        from ui.task import TaskPanel

        p = TaskPanel(task_store)
        fired = []
        p.task_changed.connect(lambda: fired.append(1))
        p._input.setText("Signal test")
        p._add_task()
        assert len(fired) >= 1
        p.close()

    def test_clear_done_button(self, qapp, task_store):
        from ui.task import TaskPanel

        t = task_store.add("To clear")
        task_store.toggle_done(t["id"])
        p = TaskPanel(task_store)
        p._clear_done()
        assert task_store.done_count() == 0
        p.close()


# ── Individual widget components ──────────────────────────────────────────────


class TestArcProgressRing:
    def test_set_state(self, qapp):
        from ui.app.progress_ring import ArcProgressRing

        arc = ArcProgressRing()
        arc.setState("12:34", "Session", "3", 0.75)
        assert arc._time_text == "12:34"
        assert arc._sub_text == "Session"
        assert arc._progress == 0.75

    def test_progress_clamped(self, qapp):
        from ui.app.progress_ring import ArcProgressRing

        arc = ArcProgressRing()
        arc.setState("00:00", "", "", 1.5)
        assert arc._progress == 1.0
        arc.setState("00:00", "", "", -0.5)
        assert arc._progress == 0.0


class TestSessionDots:
    def test_set_state(self, qapp):
        from ui.app.session_dots import SessionDots

        d = SessionDots(total=4)
        d.setState(2)
        assert d._completed == 2

    def test_completed_wraps(self, qapp):
        from ui.app.session_dots import SessionDots

        d = SessionDots(total=4)
        d.setState(5)  # 5 % (4+1) = 0
        assert d._completed == 0

    def test_set_total(self, qapp):
        from ui.app.session_dots import SessionDots

        d = SessionDots(total=4)
        d.setTotal(8)
        assert d._total == 8


class TestFooterStrip:
    def test_set_state(self, qapp):
        from ui.app.footer import FooterStrip

        f = FooterStrip()
        f.setState(completed_today=5, active_page=2)
        assert f._completed_today == 5
        assert f._active_page == 2


class TestTaskCard:
    def test_set_task(self, qapp):
        from ui.app.task_card import TaskCard

        tc = TaskCard()
        tc.setTask("Write tests", streak=7)
        assert tc._task_name == "Write tests"
        assert tc._streak == 7

    def test_default_name(self, qapp):
        from ui.app.task_card import TaskCard

        tc = TaskCard()
        assert isinstance(tc._task_name, str)
        assert len(tc._task_name) > 0


class TestSectionCardAndRowItem:
    def test_section_card_instantiation(self, qapp):
        from ui.settings.cards import SectionCard

        c = SectionCard("My Section")
        assert c is not None

    def test_row_item_instantiation(self, qapp):
        from PyQt6.QtWidgets import QLabel

        from ui.settings.cards import RowItem

        ctrl = QLabel("value")
        row = RowItem("⏱", "Title", "Sub label", ctrl)
        assert row is not None

    def test_row_item_without_control(self, qapp):
        from ui.settings.cards import RowItem

        row = RowItem("✓", "No control")
        assert row is not None

    def test_section_card_add_row(self, qapp):
        from ui.settings.cards import RowItem, SectionCard

        c = SectionCard("Test")
        r = RowItem("🔔", "Notif", "desc")
        c.add_row(r)  # must not raise
