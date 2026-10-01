from __future__ import annotations

from PyQt6.QtGui import QColor, QFont

# ── Hex strings (for QSS stylesheets) ─────────────────────────────────────────
HEX_BG = "#151B27"
HEX_CARD_BG = "rgba(13, 20, 32, 0.93)"
HEX_BORDER = "rgba(255, 255, 255, 0.12)"
HEX_TEXT = "#F7FAFF"
HEX_MUTED = "#AEB8C9"
HEX_DIM = "#7B879A"
HEX_ACCENT = "#9EE7FF"
HEX_ACCENT2 = "#50C8F3"
HEX_GREEN = "#9BE8B8"
HEX_PURPLE = "#C69EFF"
HEX_DONE_BG = "rgba(155, 232, 184, 0.07)"
HEX_ACTIVE_BG = "rgba(158, 231, 255, 0.09)"

# ── QColor objects (for QPainter routines) ─────────────────────────────────────
C_BG = QColor(0x15, 0x1B, 0x27)
C_CARD_BG = QColor(13, 20, 32, 237)
C_BORDER = QColor(255, 255, 255, 31)
C_BORDER_LIGHT = QColor(255, 255, 255, 45)
C_TEXT = QColor(0xF7, 0xFA, 0xFF)
C_MUTED = QColor(0xAE, 0xB8, 0xC9)
C_DIM = QColor(0x7B, 0x87, 0x9A)
C_ACCENT = QColor(0x9E, 0xE7, 0xFF)
C_ACCENT2 = QColor(0x50, 0xC8, 0xF3)
C_GREEN = QColor(0x9B, 0xE8, 0xB8)
C_PURPLE = QColor(0xC6, 0x9E, 0xFF)


def app_font(
    size: int,
    weight: QFont.Weight = QFont.Weight.Normal,
    family: str = "Segoe UI",
) -> QFont:
    """Create a consistent typography QFont."""
    return QFont(family, size, int(weight))
