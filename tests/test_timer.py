"""
Tests for core/timer.py — PomodoroTimer logic.

Covers:
  - initial state
  - tick countdown
  - toggle / pause
  - reset_phase
  - phase advancement: WORK → SHORT_BREAK → WORK → ... → LONG_BREAK
  - session counter
  - skip
  - apply_settings (while stopped and while running)
  - callbacks fired correctly
"""

from core.timer import Phase, PomodoroTimer

# ── helpers ───────────────────────────────────────────────────────────────────


def make_timer(work=10, short=5, long=15, sessions=4):
    ticks = []
    phases = []

    def on_tick(remaining, phase):
        ticks.append((remaining, phase))

    def on_phase_change(phase):
        phases.append(phase)

    t = PomodoroTimer(
        work_seconds=work,
        short_break_seconds=short,
        long_break_seconds=long,
        session_until_long_break=sessions,
        on_tick=on_tick,
        on_phase_change=on_phase_change,
    )
    return t, ticks, phases


# ── initial state ─────────────────────────────────────────────────────────────


class TestInitialState:
    def test_starts_in_work_phase(self):
        t, _, _ = make_timer()
        assert t.phase == Phase.WORK

    def test_remaining_equals_work_seconds(self):
        t, _, _ = make_timer(work=25 * 60)
        assert t.remaining == 25 * 60

    def test_not_running_initially(self):
        t, _, _ = make_timer()
        assert t.running is False

    def test_completed_sessions_zero(self):
        t, _, _ = make_timer()
        assert t.comleted_work_session == 0

    def test_durations_dict(self):
        t, _, _ = make_timer(work=10, short=5, long=15)
        d = t.durations()
        assert d[Phase.WORK] == 10
        assert d[Phase.SHORT_BREAK] == 5
        assert d[Phase.LONG_BREAK] == 15


# ── tick ──────────────────────────────────────────────────────────────────────


class TestTick:
    def test_tick_does_nothing_when_paused(self):
        t, ticks, _ = make_timer(work=10)
        t.tick()
        assert t.remaining == 10
        assert len(ticks) == 0

    def test_tick_decrements_when_running(self):
        t, ticks, _ = make_timer(work=10)
        t.running = True
        t.tick()
        assert t.remaining == 9
        assert ticks[-1] == (9, Phase.WORK)

    def test_multiple_ticks(self):
        t, ticks, _ = make_timer(work=10)
        t.running = True
        for _ in range(5):
            t.tick()
        assert t.remaining == 5
        assert len(ticks) == 5

    def test_tick_at_zero_advances_phase(self):
        t, _ticks, phases = make_timer(work=1, short=5, sessions=4)
        t.running = True
        t.tick()  # remaining → 0 then advances
        assert t.phase == Phase.SHORT_BREAK
        assert len(phases) == 1
        assert phases[0] == Phase.SHORT_BREAK


# ── toggle / pause ────────────────────────────────────────────────────────────


class TestTogglePause:
    def test_toggle_starts_timer(self):
        t, _, _ = make_timer()
        t.toggle()
        assert t.running is True

    def test_toggle_stops_timer(self):
        t, _, _ = make_timer()
        t.running = True
        t.toggle()
        assert t.running is False

    def test_pause_stops_running(self):
        t, _, _ = make_timer()
        t.running = True
        t.pause()
        assert t.running is False

    def test_pause_when_already_stopped_is_no_op(self):
        t, _, _ = make_timer()
        t.pause()
        assert t.running is False


# ── reset_phase ───────────────────────────────────────────────────────────────


class TestResetPhase:
    def test_reset_restores_remaining(self):
        t, _, _ = make_timer(work=10)
        t.running = True
        for _ in range(5):
            t.tick()
        t.reset_phase()
        assert t.remaining == 10

    def test_reset_stops_timer(self):
        t, _, _ = make_timer(work=10)
        t.running = True
        t.reset_phase()
        assert t.running is False

    def test_reset_fires_on_tick(self):
        t, ticks, _ = make_timer(work=10)
        ticks.clear()
        t.reset_phase()
        assert len(ticks) == 1
        assert ticks[0] == (10, Phase.WORK)

    def test_reset_during_break_restores_break_duration(self):
        t, _, _ = make_timer(work=1, short=5, sessions=4)
        t.running = True
        t.tick()  # advance to SHORT_BREAK
        t.running = True
        t.tick()  # consume 1 second of break
        t.reset_phase()
        assert t.remaining == 5
        assert t.phase == Phase.SHORT_BREAK


# ── phase advancement ─────────────────────────────────────────────────────────


class TestPhaseAdvancement:
    def test_work_goes_to_short_break_first(self):
        t, _, phases = make_timer(work=1, short=5, long=15, sessions=4)
        t.running = True
        t.tick()
        assert t.phase == Phase.SHORT_BREAK
        assert Phase.SHORT_BREAK in phases

    def test_short_break_goes_back_to_work(self):
        t, _, _phases = make_timer(work=1, short=1, long=15, sessions=4)
        t.running = True
        t.tick()  # WORK → SHORT_BREAK
        assert t.phase == Phase.SHORT_BREAK
        t.running = True
        t.tick()  # SHORT_BREAK → WORK
        assert t.phase == Phase.WORK

    def test_long_break_after_n_sessions(self):
        """After 4 completed work sessions, next break should be LONG_BREAK."""
        t, _, _phases = make_timer(work=1, short=1, long=15, sessions=4)
        # cycle through 4 work sessions
        for _ in range(4):
            t.running = True
            t.tick()  # WORK → break
            assert t.phase in (Phase.SHORT_BREAK, Phase.LONG_BREAK)
            if t.phase == Phase.LONG_BREAK:
                break
            t.running = True
            t.tick()  # break → WORK

        assert t.phase == Phase.LONG_BREAK

    def test_session_counter_increments_on_work_completion(self):
        t, _, _ = make_timer(work=1, short=1, sessions=4)
        t.running = True
        t.tick()  # complete one work session
        assert t.comleted_work_session == 1

    def test_long_break_goes_back_to_work(self):
        t, _, _ = make_timer(work=1, short=1, long=1, sessions=1)
        t.running = True
        t.tick()  # WORK (1 session) → LONG_BREAK (sessions=1)
        assert t.phase == Phase.LONG_BREAK
        t.running = True
        t.tick()  # LONG_BREAK → WORK
        assert t.phase == Phase.WORK


# ── skip ──────────────────────────────────────────────────────────────────────


class TestSkip:
    def test_skip_advances_phase(self):
        t, _, phases = make_timer(work=10, short=5, sessions=4)
        t.skip()
        assert t.phase == Phase.SHORT_BREAK
        assert len(phases) == 1

    def test_skip_resets_remaining(self):
        t, _, _ = make_timer(work=10, short=5, sessions=4)
        t.skip()
        assert t.remaining == 5

    def test_skip_increments_session_counter(self):
        t, _, _ = make_timer(work=10, sessions=4)
        t.skip()
        assert t.comleted_work_session == 1

    def test_skip_from_break_goes_to_work(self):
        t, _, _ = make_timer(work=1, short=1, sessions=4)
        t.running = True
        t.tick()  # go to short break
        t.skip()  # skip break → back to work
        assert t.phase == Phase.WORK


# ── apply_settings ────────────────────────────────────────────────────────────


class TestApplySettings:
    def test_apply_updates_durations(self):
        t, _, _ = make_timer(work=10, short=5, long=15)
        t.apply_settings(20, 8, 20, 3)
        assert t.work_seconds == 20
        assert t.short_break_seconds == 8
        assert t.long_break_seconds == 20
        assert t.session_until_long_break == 3

    def test_apply_when_stopped_resets_remaining(self):
        t, _, _ = make_timer(work=10)
        t.apply_settings(30, 5, 15, 4)
        assert t.remaining == 30

    def test_apply_when_running_does_not_change_remaining(self):
        t, _, _ = make_timer(work=10)
        t.running = True
        t.tick()  # remaining = 9
        t.apply_settings(30, 5, 15, 4)
        # running → remaining stays at 9
        assert t.remaining == 9

    def test_apply_fires_on_tick_when_stopped(self):
        t, ticks, _ = make_timer(work=10)
        ticks.clear()
        t.apply_settings(30, 5, 15, 4)
        assert ticks[-1][0] == 30

    def test_apply_does_not_fire_on_tick_when_running(self):
        t, ticks, _ = make_timer(work=10)
        t.running = True
        ticks.clear()
        t.apply_settings(30, 5, 15, 4)
        assert len(ticks) == 0


# ── callbacks ─────────────────────────────────────────────────────────────────


class TestCallbacks:
    def test_on_tick_called_each_tick(self):
        t, ticks, _ = make_timer(work=5)
        t.running = True
        for _ in range(3):
            t.tick()
        assert len(ticks) == 3

    def test_on_phase_change_called_on_advance(self):
        t, _, phases = make_timer(work=1, short=5, sessions=4)
        t.running = True
        t.tick()
        assert len(phases) == 1

    def test_callbacks_receive_correct_phase(self):
        t, ticks, _phases = make_timer(work=1, short=5, sessions=4)
        t.running = True
        t.tick()
        # on_tick after advance should show short_break with full duration
        last_tick_remaining, last_tick_phase = ticks[-1]
        assert last_tick_phase == Phase.SHORT_BREAK
        assert last_tick_remaining == 5
