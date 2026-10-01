from __future__ import annotations

from collections.abc import Callable

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from core.timer import Phase
from ui.app.constants import (
    C_ACTIVE_BDR,
    C_ACTIVE_TAB,
    C_MUTED,
    C_TAB_BORDER,
    C_TAB_CONT,
    C_TEXT,
    app_font,
)


class DarkTabButton(QPushButton):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        self._label = label
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(32)
        self.setMinimumWidth(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def setActive(self, active: bool) -> None:
        self._active = active
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 9.0

        if self._active:
            p.setPen(QPen(C_ACTIVE_BDR, 1.0))
            p.setBrush(QBrush(C_ACTIVE_TAB))
            p.drawRoundedRect(rect, radius, radius)
            text_color = C_TEXT
        else:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            text_color = C_MUTED

        p.setPen(text_color)
        p.setFont(app_font(10, QFont.Weight.Medium))
        p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._label)
        p.end()


class TabContainer(QWidget):
    def __init__(self, content: QWidget, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.addWidget(content)
        content.setParent(self)
        content.setStyleSheet("background: transparent;")

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QPen(C_TAB_BORDER, 1.0))
        p.setBrush(QBrush(C_TAB_CONT))
        p.drawRoundedRect(rect, 12.0, 12.0)
        p.end()


class PhaseTabBar(QWidget):
    def __init__(self, on_switch_phase: Callable[[Phase], None], parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._tabs: dict[Phase, DarkTabButton] = {}

        tab_inner = QWidget()
        tab_inner.setStyleSheet("background: transparent;")
        inner_layout = QHBoxLayout(tab_inner)
        inner_layout.setContentsMargins(3, 3, 3, 3)
        inner_layout.setSpacing(4)

        # Focus tab
        focus_btn = DarkTabButton("Focus")
        focus_btn.clicked.connect(lambda: on_switch_phase(Phase.WORK))
        self._tabs[Phase.WORK] = focus_btn
        inner_layout.addWidget(focus_btn)

        # Short Break tab
        short_btn = DarkTabButton("Short Break")
        short_btn.clicked.connect(lambda: on_switch_phase(Phase.SHORT_BREAK))
        self._tabs[Phase.SHORT_BREAK] = short_btn
        inner_layout.addWidget(short_btn)

        # Long Break tab
        long_btn = DarkTabButton("Long Break")
        long_btn.clicked.connect(lambda: on_switch_phase(Phase.LONG_BREAK))
        self._tabs[Phase.LONG_BREAK] = long_btn
        inner_layout.addWidget(long_btn)

        container = TabContainer(tab_inner)

        row_layout = QHBoxLayout(self)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addStretch()
        row_layout.addWidget(container)
        row_layout.addStretch()

    def sync_phase(self, phase: Phase) -> None:
        for tab_phase, btn in self._tabs.items():
            btn.setActive(tab_phase == phase)
