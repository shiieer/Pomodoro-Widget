from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.app.constants import (
    C_DIM,
    C_DOT_CUR_BDR,
    C_DOT_CUR_BG,
    C_DOT_OFF,
    C_DOT_ON,
    app_font,
)


class FooterStrip(QWidget):
    HEIGHT = 12

    def __init__(self, parent=None):
        super().__init__(parent)
        self._completed_today = 0
        self._active_page = 0
        self._total_pages = 5
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def setState(self, completed_today: int, active_page: int = 0) -> None:
        self._completed_today = completed_today
        self._active_page = active_page
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cy = self.height() / 2

        # Left: page dots
        dot_r = 4
        gap = 16
        for i in range(self._total_pages):
            cx = i * gap + dot_r
            if i == self._active_page:
                pill_w = 23
                pill_rect = QRectF(cx - pill_w / 2, cy - dot_r, pill_w, dot_r * 2)
                p.setPen(QPen(C_DOT_CUR_BDR, 1.0))
                p.setBrush(QBrush(C_DOT_CUR_BG))
                p.drawRoundedRect(pill_rect, dot_r, dot_r)
            else:
                p.setPen(Qt.PenStyle.NoPen)
                color = C_DOT_ON if i < 3 else C_DOT_OFF
                p.setBrush(QBrush(color))
                p.drawEllipse(QRectF(cx - dot_r, cy - dot_r, dot_r * 2, dot_r * 2))

        # Right: "N completed today"
        p.setPen(C_DIM)
        p.setFont(app_font(8))
        right_rect = QRectF(0, 0, self.width(), self.height())
        text = f"{self._completed_today} completed today"
        p.drawText(
            right_rect,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            text,
        )
        p.end()
