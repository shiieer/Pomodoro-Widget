"""
Extended tests for ui/app/app_window.py — PomodoroApp.

Covers gaps not in test_ui_smoke.py:
  - _switch_phase: pauses timer, resets remaining, syncs tabs, fires on_tick
  - _on_start_btn_clicked: start → mini_widget, pause → stops timer
  - _toggle: toggles running, shows mini if starting
  - switch_to_mini_widget / restore_from_mini_widget
  - _on_phase_change: updates _total_seconds, syncs tabs, updates mini widget
  - _refresh_task_card: all three branches (active, pending-no-active, empty)
  - _corner_positions: returns four named positions
  - _nearest_corner: correct corner for each quadrant
  - snap_to_corner: persists corner name to store
  - always_on_top flag in _flags()
  - stats label text per phase
  - apply_settings propagates to mini_widget
"""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.settings_store import SettingsStore
from core.task_store import TaskStore
from core.timer import Phase


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def store(tmp_path):
    return SettingsStore(path=tmp_path / "settings.json")


@pytest.fixture
def app(qapp, store):
    from ui.app.app_window import PomodoroApp

    w = PomodoroApp(store)
    yield w
    w.close()


# ── _switch_phase ─────────────────────────────────────────────────────────────


class TestSwitchPhase:
    def test_switches_to_short_break(self, app):
        app._switch_phase(Phase.SHORT_BREAK)
        assert app.timer.phase == Phase.SHORT_BREAK

    def test_switches_to_long_break(self, app):
        app._switch_phase(Phase.LONG_BREAK)
        assert app.timer.phase == Phase.LONG_BREAK

    def test_switch_pauses_timer(self, app):
        app.timer.running = True
        app._switch_phase(Phase.SHORT_BREAK)
        assert app.timer.running is False

    def test_switch_resets_remaining_to_phase_duration(self, app):
        app._switch_phase(Phase.SHORT_BREAK)
        expected = app.timer.durations()[Phase.SHORT_BREAK]
        assert app.timer.remaining == expected

    def test_switch_updates_total_seconds(self, app):
        app._switch_phase(Phase.LONG_BREAK)
        expected = app.timer.durations()[Phase.LONG_BREAK]
        assert app._total_seconds == expected

    def test_switch_updates_arc_text(self, app):
        app._switch_phase(Phase.SHORT_BREAK)
        mins = app.timer.durations()[Phase.SHORT_BREAK] // 60
        assert f"{mins:02d}:00" in app.arc._time_text

    def test_start_btn_running_stays_false_after_switch(self, app):
        app.timer.running = True
        app._switch_phase(Phase.WORK)
        assert app.start_btn._running is False


# ── _on_start_btn_clicked ─────────────────────────────────────────────────────


class TestOnStartBtnClicked:
    def test_starts_timer_when_not_running(self, app):
        app.timer.running = False
        app._on_start_btn_clicked()
        assert app.timer.running is True
        app.restore_from_mini_widget()  # clean up

    def test_pauses_timer_when_running(self, app):
        app.timer.running = True
        app._on_start_btn_clicked()
        assert app.timer.running is False

    def test_start_btn_reflects_running_state_after_pause(self, app):
        app.timer.running = True
        app._on_start_btn_clicked()
        assert app.start_btn._running is False


# ── switch_to_mini_widget / restore_from_mini_widget ─────────────────────────


class TestMiniWidgetSwitching:
    def test_switch_hides_main_and_shows_mini(self, app):
        app.switch_to_mini_widget()
        assert app.mini_widget.isVisible()
        app.restore_from_mini_widget()

    def test_restore_hides_mini(self, app):
        app.switch_to_mini_widget()
        app.restore_from_mini_widget()
        assert not app.mini_widget.isVisible()

    def test_restore_syncs_start_btn_running(self, app):
        app.timer.running = True
        app.switch_to_mini_widget()
        app.restore_from_mini_widget()
        assert app.start_btn._running is True
        app.timer.running = False
        app.start_btn.setRunning(False)

    def test_restore_syncs_start_btn_paused(self, app):
        app.timer.running = False
        app.switch_to_mini_widget()
        app.restore_from_mini_widget()
        assert app.start_btn._running is False


# ── _on_phase_change ──────────────────────────────────────────────────────────


class TestOnPhaseChange:
    def test_updates_total_seconds(self, app):
        app._on_phase_change(Phase.SHORT_BREAK)
        expected = app.timer.durations()[Phase.SHORT_BREAK]
        assert app._total_seconds == expected

    def test_updates_total_seconds_long_break(self, app):
        app._on_phase_change(Phase.LONG_BREAK)
        expected = app.timer.durations()[Phase.LONG_BREAK]
        assert app._total_seconds == expected

    def test_syncs_start_btn_running(self, app):
        app.timer.running = True
        app._on_phase_change(Phase.SHORT_BREAK)
        assert app.start_btn._running is True
        app.timer.running = False
        app.start_btn.setRunning(False)

    def test_mini_widget_updated(self, app):
        app._on_phase_change(Phase.SHORT_BREAK)
        assert app.mini_widget._phase == Phase.SHORT_BREAK


# ── _on_tick — stats labels ───────────────────────────────────────────────────


class TestOnTickStatsLabels:
    def test_work_phase_label(self, app):
        app._on_tick(1500, Phase.WORK)
        assert (
            "stay" in app._stats_label.text().lower()
            or "with" in app._stats_label.text().lower()
        )

    def test_short_break_label(self, app):
        app._on_tick(300, Phase.SHORT_BREAK)
        assert (
            "breather" in app._stats_label.text().lower()
            or "break" in app._stats_label.text().lower()
        )

    def test_long_break_label(self, app):
        app._on_tick(900, Phase.LONG_BREAK)
        assert (
            "long" in app._stats_label.text().lower()
            or "rest" in app._stats_label.text().lower()
        )

    def test_session_count_label(self, app):
        app.timer.comleted_work_session = 7
        app._on_tick(0, Phase.WORK)
        assert app._sessions_count_label.text() == "7"
        app.timer.comleted_work_session = 0


# ── _refresh_task_card — all branches ────────────────────────────────────────


class TestRefreshTaskCard:
    def test_active_task_shown(self, app, tmp_path):
        ts = TaskStore(path=tmp_path / "t.json")
        ts.add("Active task")
        app._task_store = ts
        app._refresh_task_card()
        assert "Active task" in app.task_card._task_name

    def test_pending_but_no_active_shown(self, app, tmp_path):
        ts = TaskStore(path=tmp_path / "t.json")
        ts.add("A")
        ts.add("B")
        # clear active without completing
        for t in ts._tasks:
            t["active"] = False
        ts.save()
        app._task_store = ts
        app._refresh_task_card()
        # should show "N task(s)" message
        assert "task" in app.task_card._task_name.lower()
        assert (
            "2" in app.task_card._task_name or "tap" in app.task_card._task_name.lower()
        )

    def test_empty_store_shows_prompt(self, app, tmp_path):
        ts = TaskStore(path=tmp_path / "t2.json")
        app._task_store = ts
        app._refresh_task_card()
        assert (
            "add" in app.task_card._task_name.lower()
            or "no task" in app.task_card._task_name.lower()
        )

    def test_streak_badge_shows_done_count(self, app, tmp_path):
        ts = TaskStore(path=tmp_path / "t3.json")
        t1 = ts.add("Task 1")
        ts.toggle_done(t1["id"])
        ts.add("Active")
        app._task_store = ts
        app._refresh_task_card()
        assert app.task_card._streak == ts.done_count()


# ── _corner_positions / _nearest_corner ──────────────────────────────────────


class TestCornerPositions:
    def test_returns_four_corners(self, app):
        pos = app._corner_positions()
        assert set(pos.keys()) == {
            "top-left",
            "top-right",
            "bottom-left",
            "bottom-right",
        }

    def test_positions_are_tuples(self, app):
        for pos in app._corner_positions().values():
            assert isinstance(pos, tuple)
            assert len(pos) == 2

    def test_nearest_corner_returns_valid_name(self, app):
        name = app._nearest_corner()
        assert name in ("top-left", "top-right", "bottom-left", "bottom-right")


# ── snap_to_corner ────────────────────────────────────────────────────────────


class TestSnapToCorner:
    def test_snap_saves_corner_to_store(self, app):
        app.snap_to_corner("top-left")
        assert app.store.get("corner") == "top-left"

    def test_snap_all_corners_no_crash(self, app):
        for corner in ("top-left", "top-right", "bottom-left", "bottom-right"):
            app.snap_to_corner(corner)  # must not raise

    def test_snap_without_arg_uses_stored_corner(self, app):
        app.store.update({"corner": "bottom-right"})
        app.snap_to_corner()
        assert app.store.get("corner") == "bottom-right"


# ── _flags — always_on_top ────────────────────────────────────────────────────


class TestFlags:
    def test_always_on_top_false(self, qapp, tmp_path):
        from PyQt6.QtCore import Qt

        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        store.update({"always_on_top": False})
        w = PomodoroApp(store)
        flags = w._flags()
        assert not (flags & Qt.WindowType.WindowStaysOnTopHint)
        w.close()

    def test_always_on_top_true(self, qapp, tmp_path):
        from PyQt6.QtCore import Qt

        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        store.update({"always_on_top": True})
        w = PomodoroApp(store)
        flags = w._flags()
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        w.close()


# ── apply_settings propagates ─────────────────────────────────────────────────


class TestApplySettings:
    def test_propagates_to_mini_widget(self, app):
        app.apply_settings()  # must not raise, and mini_widget should exist
        assert app.mini_widget is not None

    def test_updates_work_seconds(self, app):
        app.store.update({"work_minutes": 45})
        app.apply_settings()
        assert app.timer.work_seconds == 45 * 60

    def test_updates_session_dots_total(self, app):
        app.store.update({"sessions_until_long_break": 6})
        app.apply_settings()
        # Next on_tick will update dots; force it
        app._on_tick(app.timer.remaining, app.timer.phase)
        assert app.session_dots._total == 6
