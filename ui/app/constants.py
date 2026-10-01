from __future__ import annotations

from PyQt6.QtGui import QColor

from core.timer import Phase
from ui.common import (
    C_ACCENT,
    C_ACCENT2,
    C_BG,
    C_BORDER,
    C_DIM,
    C_GREEN,
    C_MUTED,
    C_PURPLE,
    C_TEXT,
    HDivider,
    app_font,
)

# ── App-specific palette variations ──────────────────────────────────────────
C_BG_SOLID = C_BG
C_HEADER_DIV = QColor(255, 255, 255, 31)
C_GLOW_PURPLE = QColor(0x77, 0x59, 0xD4, 69)
C_GLOW_CYAN = QColor(0x2C, 0xBF, 0xE3, 94)
C_TAB_CONT = QColor(255, 255, 255, 18)
C_TAB_BORDER = QColor(255, 255, 255, 31)
C_ACTIVE_TAB = QColor(255, 255, 255, 23)
C_ACTIVE_BDR = QColor(255, 255, 255, 51)
C_BTN_BG = QColor(255, 255, 255, 13)
C_BTN_BORDER = QColor(255, 255, 255, 31)
C_TASK_BG = QColor(255, 255, 255, 13)
C_DOT_ON = C_ACCENT
C_DOT_OFF = QColor(255, 255, 255, 18)
C_DOT_CUR_BG = QColor(0x8C, 0xDE, 0xFF, 36)
C_DOT_CUR_BDR = C_ACCENT2

# ── Phase Metadata ────────────────────────────────────────────────────────────
PHASE_LABELS = {
    Phase.WORK: "Focus",
    Phase.SHORT_BREAK: "Short Break",
    Phase.LONG_BREAK: "Long Break",
}

PHASE_SUB = {
    Phase.WORK: "Session",
    Phase.SHORT_BREAK: "Short Break",
    Phase.LONG_BREAK: "Long Break",
}

__all__ = [
    "C_ACCENT",
    "C_ACCENT2",
    "C_ACTIVE_BDR",
    "C_ACTIVE_TAB",
    "C_BG",
    "C_BG_SOLID",
    "C_BORDER",
    "C_BTN_BG",
    "C_BTN_BORDER",
    "C_DIM",
    "C_DOT_CUR_BDR",
    "C_DOT_CUR_BG",
    "C_DOT_OFF",
    "C_DOT_ON",
    "C_GLOW_CYAN",
    "C_GLOW_PURPLE",
    "C_GREEN",
    "C_HEADER_DIV",
    "C_MUTED",
    "C_PURPLE",
    "C_TAB_BORDER",
    "C_TAB_CONT",
    "C_TASK_BG",
    "C_TEXT",
    "PHASE_LABELS",
    "PHASE_SUB",
    "HDivider",
    "app_font",
]
