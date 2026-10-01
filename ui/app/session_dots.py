from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.app.constants import (
    C_DOT_CUR_BDR,
    C_DOT_CUR_BG,
    C_DOT_OFF,
    C_DOT_ON,
)


class SessionDots(QWidget):
    DOT_R = 4
    CUR_R = 5
    SPACING = 16
    HEIGHT = 16

    def __init__(self, total: int = 4, parent=None):
        super().__init__(parent)
        self._total = total
        self._completed = 0
        self.setFixedHeight(self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._update_width()

    def _update_width(self) -> None:
        total_dots = self._total + 1
        w = total_dots * (self.DOT_R * 2) + (total_dots - 1) * (
            self.SPACING - self.DOT_R * 2
        )
        self.setFixedWidth(max(w, 80))

    def setTotal(self, total: int) -> None:
        self._total = total
        self._update_width()
        self.update()

    def setState(self, completed: int) -> None:
        self._completed = completed % (self._total + 1)
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        total_dots = self._total + 1
        dot_diam = self.DOT_R * 2
        gap = self.SPACING
        total_w = total_dots * dot_diam + (total_dots - 1) * (gap - dot_diam)
        start_x = (self.width() - total_w) / 2
        cy = self.height() / 2

        for i in range(total_dots):
            cx = start_x + i * gap + self.DOT_R

            if i < self._completed:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(C_DOT_ON))
                p.drawEllipse(
                    QRectF(cx - self.DOT_R, cy - self.DOT_R, dot_diam, dot_diam)
                )
            elif i == self._completed:
                p.setPen(QPen(C_DOT_CUR_BDR, 1.0))
                p.setBrush(QBrush(C_DOT_CUR_BG))
                r = self.CUR_R
                p.drawEllipse(QRectF(cx - r, cy - r, r * 2, r * 2))
            else:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(C_DOT_OFF))
                p.drawEllipse(
                    QRectF(cx - self.DOT_R, cy - self.DOT_R, dot_diam, dot_diam)
                )
        p.end()
