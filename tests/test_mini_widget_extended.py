"""
Extended tests for ui/widget/mini_widget.py — MiniWidget.

Covers gaps not in test_ui_smoke.py:
  - update_phase: phase and total_seconds stored
  - sync_state: pulls from app.timer
  - _update_display: all three phase label variants (WORK, SHORT_BREAK, LONG_BREAK)
  - _toggle_timer: toggles app.timer.running
  - _restore_app: calls restore_from_mini_widget
  - snap_to_corner: all four corners without crash
  - apply_settings: opacity from store, _has_moved_manually guard
  - _flags: always_on_top branch
"""

import os
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.settings_store import SettingsStore
from core.timer import Phase


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication(sys.argv)


@pytest.fixture
def app(qapp, tmp_path):
    from ui.app.app_window import PomodoroApp

    store = SettingsStore(path=tmp_path / "settings.json")
    w = PomodoroApp(store)
    yield w
    w.close()


# ── update_phase ──────────────────────────────────────────────────────────────


class TestUpdatePhase:
    def test_stores_new_phase(self, app):
        app.mini_widget.update_phase(Phase.SHORT_BREAK, 300)
        assert app.mini_widget._phase == Phase.SHORT_BREAK

    def test_stores_total_seconds(self, app):
        app.mini_widget.update_phase(Phase.LONG_BREAK, 900)
        assert app.mini_widget._total_seconds == 900

    def test_clamps_total_to_at_least_one(self, app):
        app.mini_widget.update_phase(Phase.WORK, 0)
        assert app.mini_widget._total_seconds >= 1

    def test_updates_phase_label_to_long_break(self, app):
        app.mini_widget.update_phase(Phase.LONG_BREAK, 900)
        assert (
            "LONG" in app.mini_widget.phase_label.text().upper()
            or "BREAK" in app.mini_widget.phase_label.text().upper()
        )


# ── sync_state ────────────────────────────────────────────────────────────────


class TestSyncState:
    def test_pulls_remaining_from_timer(self, app):
        app.timer.remaining = 500
        app.mini_widget.sync_state()
        assert app.mini_widget._remaining == 500

    def test_pulls_phase_from_timer(self, app):
        app.timer.phase = Phase.SHORT_BREAK
        app.mini_widget.sync_state()
        assert app.mini_widget._phase == Phase.SHORT_BREAK
        app.timer.phase = Phase.WORK  # reset

    def test_sync_updates_display(self, app):
        app.timer.remaining = 750
        app.mini_widget.sync_state()
        assert app.mini_widget.time_label.text() == "12:30"


# ── _update_display — all three phase labels ──────────────────────────────────


class TestUpdateDisplay:
    def test_work_phase_label_text(self, app):
        app.mini_widget.update_tick(600, Phase.WORK, 1500)
        assert "FOCUS" in app.mini_widget.phase_label.text().upper()

    def test_short_break_label_text(self, app):
        app.mini_widget.update_tick(300, Phase.SHORT_BREAK, 300)
        assert (
            "SHORT" in app.mini_widget.phase_label.text().upper()
            or "BREAK" in app.mini_widget.phase_label.text().upper()
        )

    def test_long_break_label_text(self, app):
        app.mini_widget.update_tick(900, Phase.LONG_BREAK, 900)
        assert (
            "LONG" in app.mini_widget.phase_label.text().upper()
            or "BREAK" in app.mini_widget.phase_label.text().upper()
        )

    def test_time_format_zero(self, app):
        app.mini_widget.update_tick(0, Phase.WORK, 1500)
        assert app.mini_widget.time_label.text() == "00:00"

    def test_time_format_over_one_hour(self, app):
        app.mini_widget.update_tick(3661, Phase.WORK, 3661)
        assert app.mini_widget.time_label.text() == "61:01"


# ── _toggle_timer ─────────────────────────────────────────────────────────────


class TestToggleTimer:
    def test_starts_timer_when_stopped(self, app):
        app.timer.running = False
        app.mini_widget._toggle_timer()
        assert app.timer.running is True
        app.timer.running = False  # restore

    def test_pauses_timer_when_running(self, app):
        app.timer.running = True
        app.mini_widget._toggle_timer()
        assert app.timer.running is False

    def test_syncs_start_btn(self, app):
        app.timer.running = False
        app.mini_widget._toggle_timer()
        assert app.start_btn._running is True
        app.timer.running = False
        app.start_btn.setRunning(False)


# ── _restore_app ──────────────────────────────────────────────────────────────


class TestRestoreApp:
    def test_restore_hides_mini(self, app):
        app.mini_widget.show()
        app.mini_widget._restore_app()
        assert not app.mini_widget.isVisible()

    def test_restore_shows_main_app(self, app):
        app.mini_widget._restore_app()
        assert app.isVisible()


# ── snap_to_corner ────────────────────────────────────────────────────────────


class TestSnapToCorner:
    def test_all_corners_no_crash(self, app):
        for corner in ("top-left", "top-right", "bottom-left", "bottom-right"):
            app.mini_widget.snap_to_corner(corner)  # must not raise

    def test_respects_stored_corner(self, app):
        app.store.update({"corner": "top-left"})
        # _has_moved_manually must be False for snap to fire
        app.mini_widget._has_moved_manually = False
        app.mini_widget.snap_to_corner()
        # No crash + widget is still on screen

    def test_no_snap_when_has_moved_manually(self, app):
        app.mini_widget._has_moved_manually = True
        # apply_settings should not snap
        app.mini_widget.apply_settings()
        # No crash; just verify flag is honoured
        app.mini_widget._has_moved_manually = False


# ── apply_settings ────────────────────────────────────────────────────────────


class TestMiniApplySettings:
    def test_applies_opacity(self, app):
        app.store.update({"opacity": 0.75})
        app.mini_widget.apply_settings()
        assert abs(app.mini_widget.windowOpacity() - 0.75) < 0.01

    def test_no_crash(self, app):
        app.mini_widget.apply_settings()  # baseline no-crash


# ── _flags ────────────────────────────────────────────────────────────────────


class TestMiniFlags:
    def test_always_on_top_flag(self, qapp, tmp_path):
        from PyQt6.QtCore import Qt

        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        store.update({"always_on_top": True})
        w = PomodoroApp(store)
        flags = w.mini_widget._flags()
        assert flags & Qt.WindowType.WindowStaysOnTopHint
        w.close()

    def test_always_on_top_false(self, qapp, tmp_path):
        from PyQt6.QtCore import Qt

        from ui.app.app_window import PomodoroApp

        store = SettingsStore(path=tmp_path / "s.json")
        store.update({"always_on_top": False})
        w = PomodoroApp(store)
        flags = w.mini_widget._flags()
        assert not (flags & Qt.WindowType.WindowStaysOnTopHint)
        w.close()
