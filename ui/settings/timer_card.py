from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_SETTINGS
from ui.settings.cards import Card


class TimerCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        card = Card("Get ready to focus")

        subtitle = QLabel("Set work and break lengths for the widget.")
        subtitle.setObjectName("Muted")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.work = QSpinBox()
        self.work.setRange(1, 180)
        self.work.setValue(store.get("work_minutes"))
        self.work.setSuffix(" mins")
        self.work.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.work.setFixedWidth(140)
        self.work.valueChanged.connect(self._update_break_hint)

        time_row = QHBoxLayout()
        time_row.addStretch()
        time_row.addWidget(self.work)
        time_row.addStretch()
        time_wrap = QWidget()
        time_wrap.setLayout(time_row)

        self.break_hint = QLabel()
        self.break_hint.setObjectName("Muted")
        self.break_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.skip_breaks = QCheckBox("Skip breaks")
        self.skip_breaks.setChecked(bool(store.get("skip_breaks", False)))

        breaks = QWidget()
        breaks_form = QVBoxLayout(breaks)
        breaks_form.setContentsMargins(0, 8, 0, 0)
        breaks_form.setSpacing(8)

        self.short_break = QSpinBox()
        self.short_break.setRange(1, 60)
        self.short_break.setValue(store.get("short_break_minutes"))
        self.short_break.setSuffix(" min")

        self.long_break = QSpinBox()
        self.long_break.setRange(1, 60)
        self.long_break.setValue(store.get("long_break_minutes"))
        self.long_break.setSuffix(" min")

        self.until_long = QSpinBox()
        self.until_long.setRange(1, 12)
        self.until_long.setValue(store.get("sessions_until_long_break"))
        self.until_long.valueChanged.connect(self._update_break_hint)

        for label, widget in (
            ("Short break", self.short_break),
            ("Long break", self.long_break),
            ("Sessions until long break", self.until_long),
        ):
            row = QHBoxLayout()
            text = QLabel(label)
            text.setObjectName("Muted")
            row.addWidget(text)
            row.addStretch()
            row.addWidget(widget)
            wrap = QWidget()
            wrap.setLayout(row)
            breaks_form.addWidget(wrap)

        self.save_hint = QPushButton("Save to apply on the widget")
        self.save_hint.setObjectName("Accent")
        self.save_hint.setEnabled(False)

        reset = QPushButton("Reset timer")
        reset.clicked.connect(self.reset)

        card.add(subtitle)
        card.add(time_wrap)
        card.add(self.break_hint)
        card.add(self.skip_breaks)
        card.add(breaks)
        card.add(self.save_hint)
        card.add(reset)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        layout.addStretch()
        self._update_break_hint()

    def _update_break_hint(self) -> None:
        n = max(0, self.until_long.value() - 1)
        if n <= 0:
            self.break_hint.setText("You'll have a long break after this session.")
        elif n == 1:
            self.break_hint.setText("You'll have 1 break.")
        else:
            self.break_hint.setText(
                f"You'll have {n} short breaks before a long break."
            )

    def reset(self) -> None:
        d = DEFAULT_SETTINGS
        self.work.setValue(d["work_minutes"])
        self.short_break.setValue(d["short_break_minutes"])
        self.long_break.setValue(d["long_break_minutes"])
        self.until_long.setValue(d["sessions_until_long_break"])
        self.skip_breaks.setChecked(False)
        self._update_break_hint()

    def values(self) -> dict:
        return {
            "work_minutes": self.work.value(),
            "short_break_minutes": self.short_break.value(),
            "long_break_minutes": self.long_break.value(),
            "sessions_until_long_break": self.until_long.value(),
            "skip_breaks": self.skip_breaks.isChecked(),
        }
