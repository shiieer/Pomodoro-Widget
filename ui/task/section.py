from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui.task.style import C_BORDER, C_DIM


class TaskSection(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskSection")

        self._body = QVBoxLayout(self)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)

        hdr = QLabel(f"  {title}")
        hdr.setStyleSheet(
            f"color: {C_DIM}; font-size: 11px; font-weight: 600;"
            " text-transform: uppercase; letter-spacing: 1px;"
            " padding: 10px 16px 8px 16px; background: transparent;"
        )
        self._body.addWidget(hdr)
        self._divider_needed = False

    def add_row(self, w: QWidget) -> None:
        if self._divider_needed:
            line = QFrame()
            line.setFixedHeight(1)
            line.setStyleSheet(f"background: {C_BORDER};")
            self._body.addWidget(line)
        self._body.addWidget(w)
        self._divider_needed = True

    def is_empty(self) -> bool:
        # count only QWidget rows (not the header label)
        return self._body.count() <= 1
