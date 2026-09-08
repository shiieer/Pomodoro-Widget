from enum import Enum
from typing import Callable


class Phase(str, Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class PomodoroTimer:
    def __init__(
        self,
        work_seconds: int,
        short_break_seconds: int,
        long_break_seconds: int,
        session_until_long_break: int,
        on_tick: Callable[[int, "Phase"], None],
        on_phase_change: Callable[["Phase"], None],
    ):
        self.work_seconds = work_seconds
        self.short_break_seconds = short_break_seconds
        self.long_break_seconds = long_break_seconds
        self.session_until_long_break = session_until_long_break
        self.on_tick = on_tick
        self.on_phase_change = on_phase_change

        self.phase = Phase.WORK
        self.remaining = work_seconds
        self.comleted_work_session = 0
        self.running = False

    def durations(self) -> dict[Phase, int]:
        return {
            Phase.WORK: self.work_seconds,
            Phase.SHORT_BREAK: self.short_break_seconds,
            Phase.LONG_BREAK: self.long_break_seconds,
        }

    def toggle(self) -> None:
        self.running = not self.running

    def pause(self) -> None:
        self.running = False

    def reset_phase(self) -> None:
        self.running = False
        self.remaining = self.durations()[self.phase]
        self.on_tick(self.remaining, self.phase)

    def skip(self) -> None:
        self._advance_phase()

    def apply_settings(
        self,
        work_seconds: int,
        short_break_seconds: int,
        long_break_seconds: int,
        sessions_until_long_break: int,
    ) -> None:
        self.work_seconds = work_seconds
        self.short_break_seconds = short_break_seconds
        self.long_break_seconds = long_break_seconds
        self.session_until_long_break = sessions_until_long_break
        if not self.running:
            self.remaining = self.durations()[self.phase]
            self.on_tick(self.remaining, self.phase)

    def tick(self) -> None:
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            self.on_tick(self.remaining, self.phase)
            return
        self._advance_phase()

    def _advance_phase(self) -> None:
        if self.phase == Phase.WORK:
            self.comleted_work_session += 1
            if self.comleted_work_session % self.session_until_long_break == 0:
                self.phase = Phase.LONG_BREAK
            else:
                self.phase = Phase.SHORT_BREAK
        else:
            self.phase = Phase.WORK

        self.remaining = self.durations()[self.phase]
        self.on_phase_change(self.phase)
        self.on_tick(self.remaining, self.phase)
