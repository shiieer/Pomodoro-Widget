from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.common.theme import C_BORDER


class HDivider(QWidget):
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self._color = color or C_BORDER
        self.setFixedHeight(1)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setPen(QPen(self._color, 1.0))
        p.drawLine(0, 0, self.width(), 0)
        p.end()
