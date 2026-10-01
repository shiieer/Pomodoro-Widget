from PyQt6.QtWidgets import (
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_SETTINGS
from ui.settings.cards import RowItem, ScrollPage, SectionCard, ToggleSwitch


class TimerCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)

        # ── work duration ─────────────────────────────────────────────────────
        self.work = QSpinBox()
        self.work.setRange(1, 180)
        self.work.setValue(store.get("work_minutes"))
        self.work.setSuffix(" min")
        self.work.setFixedWidth(90)

        # ── short break ───────────────────────────────────────────────────────
        self.short_break = QSpinBox()
        self.short_break.setRange(1, 60)
        self.short_break.setValue(store.get("short_break_minutes"))
        self.short_break.setSuffix(" min")
        self.short_break.setFixedWidth(90)

        # ── long break ────────────────────────────────────────────────────────
        self.long_break = QSpinBox()
        self.long_break.setRange(1, 60)
        self.long_break.setValue(store.get("long_break_minutes"))
        self.long_break.setSuffix(" min")
        self.long_break.setFixedWidth(90)

        # ── sessions until long break ─────────────────────────────────────────
        self.until_long = QSpinBox()
        self.until_long.setRange(1, 12)
        self.until_long.setValue(store.get("sessions_until_long_break"))
        self.until_long.setFixedWidth(90)

        # ── skip breaks toggle ────────────────────────────────────────────────
        self.skip_toggle = ToggleSwitch(bool(store.get("skip_breaks", False)))

        # ── card ──────────────────────────────────────────────────────────────
        card = SectionCard("Timer")
        card.add_row(
            RowItem("⏱", "Work duration", "Length of each focus session", self.work)
        )
        card.add_row(
            RowItem(
                "☕", "Short break", "Break between focus sessions", self.short_break
            )
        )
        card.add_row(
            RowItem(
                "🌙",
                "Long break",
                "Longer rest after several sessions",
                self.long_break,
            )
        )
        card.add_row(
            RowItem(
                "🔁",
                "Sessions until long break",
                "How many work sessions before a long break",
                self.until_long,
            )
        )
        card.add_row(
            RowItem(
                "⏭",
                "Skip breaks",
                "Go straight back to focus after each session",
                self.skip_toggle,
            )
        )

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)
        lay.addWidget(card)
        lay.addStretch()

        page = ScrollPage(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)

    def reset(self) -> None:
        d = DEFAULT_SETTINGS
        self.work.setValue(d["work_minutes"])
        self.short_break.setValue(d["short_break_minutes"])
        self.long_break.setValue(d["long_break_minutes"])
        self.until_long.setValue(d["sessions_until_long_break"])
        self.skip_toggle.setChecked(False)

    def values(self) -> dict:
        return {
            "work_minutes": self.work.value(),
            "short_break_minutes": self.short_break.value(),
            "long_break_minutes": self.long_break.value(),
            "sessions_until_long_break": self.until_long.value(),
            "skip_breaks": self.skip_toggle.isChecked(),
        }
