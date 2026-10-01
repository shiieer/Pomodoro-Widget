"""
Tests for the task UI components:
  - ui/task/task_row.py  — TaskRow (full class, zero prior coverage)
  - ui/task/section.py   — TaskSection (is_empty, add_row divider logic)
  - ui/task/panel.py     — TaskPanel extended (refresh branches, count label, signal)
  - ui/settings/sidebar.py — SettingsSidebar page_changed signal
  - ui/settings/settings_window.py — _update_page_title, _restore_defaults
  - ui/settings/look_card.py — values() color/gif_size keys, reset() color fields
  - ui/settings/timer_card.py — values() skip_breaks key, reset() toggle
  - ui/settings/cards.py — SectionCard.add(), ScrollPage, ToggleSwitch.toggled signal
"""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QLabel

from core.settings_store import SettingsStore
from core.task_store import TaskStore


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def store(tmp_path):
    return SettingsStore(path=tmp_path / "settings.json")


@pytest.fixture
def task_store(tmp_path):
    return TaskStore(path=tmp_path / "tasks.json")


# ── TaskRow ───────────────────────────────────────────────────────────────────


class TestTaskRow:
    def _make_row(self, task, store_obj, callback):
        from ui.task.task_row import TaskRow

        return TaskRow(task, store_obj, callback)

    def test_instantiation_pending_task(self, qapp, task_store):
        t = task_store.add("Pending task")
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        assert row is not None

    def test_instantiation_active_task(self, qapp, task_store):
        t = task_store.add("Active task")  # first task → auto active
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        assert row is not None

    def test_instantiation_done_task(self, qapp, task_store):
        t = task_store.add("Done task")
        task_store.toggle_done(t["id"])
        t_updated = next(x for x in task_store.all() if x["id"] == t["id"])
        fired = []
        row = self._make_row(t_updated, task_store, lambda: fired.append(1))
        assert row is not None

    def test_toggle_done_calls_store(self, qapp, task_store):
        t = task_store.add("To toggle")
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        row._toggle_done()
        assert task_store.done_count() == 1
        assert len(fired) == 1

    def test_toggle_done_fires_callback(self, qapp, task_store):
        t = task_store.add("Callback test")
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        row._toggle_done()
        assert len(fired) >= 1

    def test_set_active_calls_store(self, qapp, task_store):
        task_store.add("A")
        t2 = task_store.add("B")
        fired = []
        row = self._make_row(t2, task_store, lambda: fired.append(1))
        row._set_active()
        assert task_store.active_task()["id"] == t2["id"]

    def test_set_active_fires_callback(self, qapp, task_store):
        task_store.add("A")
        t2 = task_store.add("B")
        fired = []
        row = self._make_row(t2, task_store, lambda: fired.append(1))
        row._set_active()
        assert len(fired) >= 1

    def test_delete_calls_store(self, qapp, task_store):
        t = task_store.add("To delete")
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        row._delete()
        assert not any(x["id"] == t["id"] for x in task_store.all())

    def test_delete_fires_callback(self, qapp, task_store):
        t = task_store.add("Delete cb")
        fired = []
        row = self._make_row(t, task_store, lambda: fired.append(1))
        row._delete()
        assert len(fired) >= 1

    def test_active_btn_absent_for_done_task(self, qapp, task_store):
        t = task_store.add("Done")
        task_store.toggle_done(t["id"])
        t_done = next(x for x in task_store.all() if x["id"] == t["id"])
        # TaskRow for done task should not have an active_btn (set_active meaningless)
        row = self._make_row(t_done, task_store, lambda: None)
        # Count buttons — done tasks should have exactly 2 (check + delete), no active btn
        from PyQt6.QtWidgets import QPushButton

        btns = row.findChildren(QPushButton)
        # check+delete = 2, no ▶ active btn
        assert len(btns) == 2

    def test_active_btn_absent_for_active_task(self, qapp, task_store):
        t = task_store.add("Active")  # first task → auto active
        row = self._make_row(t, task_store, lambda: None)
        from PyQt6.QtWidgets import QPushButton

        btns = row.findChildren(QPushButton)
        # active task: check+delete only (no ▶ btn because it's already active)
        assert len(btns) == 2

    def test_active_btn_present_for_pending_non_active_task(self, qapp, task_store):
        task_store.add("Active one")
        t2 = task_store.add("Pending one")
        row = self._make_row(t2, task_store, lambda: None)
        from PyQt6.QtWidgets import QPushButton

        btns = row.findChildren(QPushButton)
        # pending non-active: check + active(▶) + delete = 3
        assert len(btns) == 3


# ── TaskSection ───────────────────────────────────────────────────────────────


class TestTaskSection:
    def test_is_empty_when_no_rows(self, qapp):
        from ui.task.section import TaskSection

        sec = TaskSection("Test")
        assert sec.is_empty() is True

    def test_is_empty_false_after_add_row(self, qapp):
        from ui.task.section import TaskSection

        sec = TaskSection("Test")
        sec.add_row(QLabel("row"))
        assert sec.is_empty() is False

    def test_first_row_has_no_leading_divider(self, qapp):
        from ui.task.section import TaskSection

        sec = TaskSection("Test")
        before = sec._body.count()
        sec.add_row(QLabel("first"))
        after = sec._body.count()
        # exactly one widget added (no divider before first row)
        assert after - before == 1

    def test_second_row_adds_divider(self, qapp):
        from ui.task.section import TaskSection

        sec = TaskSection("Test")
        sec.add_row(QLabel("first"))
        count_after_first = sec._body.count()
        sec.add_row(QLabel("second"))
        count_after_second = sec._body.count()
        # Should have added 2: one divider + one row
        assert count_after_second - count_after_first == 2


# ── TaskPanel extended ────────────────────────────────────────────────────────


class TestTaskPanelExtended:
    def test_count_label_shows_pending(self, qapp, task_store):
        from ui.task.panel import TaskPanel

        task_store.add("A")
        task_store.add("B")
        p = TaskPanel(task_store)
        assert "2" in p._count_lbl.text() or "pending" in p._count_lbl.text()
        p.close()

    def test_count_label_shows_done_when_all_done(self, qapp, task_store):
        from ui.task.panel import TaskPanel

        t = task_store.add("Done one")
        task_store.toggle_done(t["id"])
        p = TaskPanel(task_store)
        assert "done" in p._count_lbl.text().lower() or "1" in p._count_lbl.text()
        p.close()

    def test_count_label_empty_when_no_tasks(self, qapp, tmp_path):
        from ui.task.panel import TaskPanel

        ts = TaskStore(path=tmp_path / "empty.json")
        p = TaskPanel(ts)
        # no tasks → empty label or blank
        assert p._count_lbl.text() == "" or "0" in p._count_lbl.text()
        p.close()

    def test_task_changed_fired_on_refresh(self, qapp, task_store):
        from ui.task.panel import TaskPanel

        p = TaskPanel(task_store)
        fired = []
        p.task_changed.connect(lambda: fired.append(1))
        p._refresh()
        assert len(fired) >= 1
        p.close()

    def test_refresh_shows_empty_label_when_no_tasks(self, qapp, tmp_path):
        from ui.task.panel import TaskPanel

        ts = TaskStore(path=tmp_path / "empty2.json")
        p = TaskPanel(ts)
        # Find QLabel children in the scroll area
        from PyQt6.QtWidgets import QLabel

        labels = p._list_widget.findChildren(QLabel)
        texts = [lbl.text() for lbl in labels]
        assert any("no task" in t.lower() or "add" in t.lower() for t in texts)
        p.close()

    def test_add_then_clear_done(self, qapp, task_store):
        from ui.task.panel import TaskPanel

        p = TaskPanel(task_store)
        p._input.setText("Clear me")
        p._add_task()
        t = task_store.active_task()
        task_store.toggle_done(t["id"])
        p._clear_done()
        assert task_store.done_count() == 0
        p.close()


# ── SettingsSidebar — page_changed signal ────────────────────────────────────


class TestSettingsSidebar:
    def test_page_changed_fires_on_row_change(self, qapp):
        from ui.settings.sidebar import SettingsSidebar

        sb = SettingsSidebar()
        received = []
        sb.page_changed.connect(lambda i: received.append(i))
        sb.setCurrentRow(1)
        assert received == [1]

    def test_page_changed_fires_with_correct_index(self, qapp):
        from ui.settings.sidebar import SettingsSidebar

        sb = SettingsSidebar()
        received = []
        sb.page_changed.connect(lambda i: received.append(i))
        sb.setCurrentRow(2)
        assert 2 in received

    def test_initial_row_is_zero(self, qapp):
        from ui.settings.sidebar import SettingsSidebar

        sb = SettingsSidebar()
        assert sb.currentRow() == 0


# ── SettingsWindow — _update_page_title, _restore_defaults ───────────────────


class TestSettingsWindowExtended:
    def test_update_page_title_timer(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w._update_page_title(0)
        assert "timer" in w._page_title.text().lower()
        w.close()

    def test_update_page_title_look(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w._update_page_title(1)
        assert (
            "look" in w._page_title.text().lower()
            or "appear" in w._page_title.text().lower()
        )
        w.close()

    def test_update_page_title_media(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w._update_page_title(2)
        assert "media" in w._page_title.text().lower()
        w.close()

    def test_sidebar_change_updates_page_title(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.sidebar.setCurrentRow(1)
        assert w.pages.currentIndex() == 1
        w.close()

    def test_restore_defaults_resets_timer_work_minutes(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.timer_card.work.setValue(99)
        w._restore_defaults()
        assert w.timer_card.work.value() == DEFAULT_SETTINGS["work_minutes"]
        w.close()

    def test_restore_defaults_resets_look_opacity(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.look_card.opacity.setValue(0.3)
        w._restore_defaults()
        assert abs(w.look_card.opacity.value() - DEFAULT_SETTINGS["opacity"]) < 0.01
        w.close()


# ── LookCard.values() — color and gif_size keys ──────────────────────────────


class TestLookCardValues:
    def test_values_contains_timer_color(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.look_card.values()
        assert "timer_color" in v
        w.close()

    def test_values_contains_label_color(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.look_card.values()
        assert "label_color" in v
        w.close()

    def test_values_contains_bg_color(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.look_card.values()
        assert "bg_color" in v
        w.close()

    def test_values_contains_gif_size(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.look_card.values()
        assert "gif_size" in v
        w.close()

    def test_reset_resets_timer_color(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.look_card._timer_color_edit.setText("#000000")
        w.look_card.reset()
        assert w.look_card._timer_color_edit.text() == DEFAULT_SETTINGS["timer_color"]
        w.close()

    def test_reset_resets_bg_color(self, qapp, store):
        from config import DEFAULT_SETTINGS
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.look_card._bg_color_edit.setText("#000000")
        w.look_card.reset()
        assert w.look_card._bg_color_edit.text() == DEFAULT_SETTINGS["bg_color"]
        w.close()


# ── TimerCard.values() — skip_breaks key; reset() — toggle ───────────────────


class TestTimerCardExtended:
    def test_values_contains_skip_breaks(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.timer_card.values()
        assert "skip_breaks" in v
        w.close()

    def test_skip_breaks_value_is_bool(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        v = w.timer_card.values()
        assert isinstance(v["skip_breaks"], bool)
        w.close()

    def test_reset_sets_skip_toggle_false(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.timer_card.skip_toggle.setChecked(True)
        w.timer_card.reset()
        assert w.timer_card.skip_toggle.isChecked() is False
        w.close()

    def test_skip_breaks_true_in_values(self, qapp, store):
        from ui.settings.settings_window import SettingsWindow

        w = SettingsWindow(store)
        w.timer_card.skip_toggle.setChecked(True)
        assert w.timer_card.values()["skip_breaks"] is True
        w.close()


# ── SectionCard.add() / ScrollPage / ToggleSwitch.toggled signal ─────────────


class TestCardsExtended:
    def test_section_card_add_no_divider(self, qapp):
        """add() convenience method adds widget without a divider."""
        from ui.settings.cards import SectionCard

        c = SectionCard("X")
        before = c._body.count()
        c.add(QLabel("plain widget"))
        after = c._body.count()
        assert after - before == 1  # no divider prepended

    def test_scroll_page_instantiation(self, qapp):
        from ui.settings.cards import ScrollPage

        content = QLabel("inner content")
        page = ScrollPage(content)
        assert page is not None

    def test_toggle_switch_toggled_signal_emits_true(self, qapp):
        from PyQt6.QtCore import QEvent, QPointF, Qt
        from PyQt6.QtGui import QMouseEvent

        from ui.settings.cards import ToggleSwitch

        ts = ToggleSwitch(False)
        received = []
        ts.toggled.connect(lambda v: received.append(v))

        # Simulate mouse press to trigger toggle
        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(ts.width() / 2, ts.height() / 2),
            QPointF(0, 0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        ts.mousePressEvent(event)
        assert len(received) == 1
        assert received[0] is True

    def test_toggle_switch_toggled_signal_emits_false(self, qapp):
        from PyQt6.QtCore import QEvent, QPointF, Qt
        from PyQt6.QtGui import QMouseEvent

        from ui.settings.cards import ToggleSwitch

        ts = ToggleSwitch(True)
        received = []
        ts.toggled.connect(lambda v: received.append(v))

        event = QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(ts.width() / 2, ts.height() / 2),
            QPointF(0, 0),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        ts.mousePressEvent(event)
        assert len(received) == 1
        assert received[0] is False

    def test_icon_circle_instantiation(self, qapp):
        from ui.settings.cards import IconCircle

        ic = IconCircle("⏱")
        assert ic is not None
        assert ic.SIZE == 26

    def test_hdivider_instantiation(self, qapp):
        from ui.settings.cards import HDivider

        d = HDivider()
        assert d.height() == 1
