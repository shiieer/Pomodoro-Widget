from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QRadialGradient,
)
from PyQt6.QtWidgets import QWidget

from ui.app.constants import C_BG, C_BORDER


class DarkCard(QWidget):
    RADIUS = 24
    MIN_WIDTH = 448

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(self.MIN_WIDTH)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, self.RADIUS, self.RADIUS)

        # ── clip to card shape ────────────────────────────────────────────────
        p.setClipPath(path)

        # Solid base fill
        p.fillPath(path, QBrush(C_BG))

        # Subtle top-to-bottom gradient overlay
        bg_grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        bg_grad.setColorAt(0.0, QColor(255, 255, 255, 8))
        bg_grad.setColorAt(1.0, QColor(0, 0, 0, 30))
        p.fillPath(path, QBrush(bg_grad))

        # Purple glow — bottom-right corner with smooth radial falloff
        gx = rect.right() - 60
        gy = rect.bottom() - 80
        purple_rad = QRadialGradient(gx, gy, 180)
        purple_rad.setColorAt(0.0, QColor(0x77, 0x59, 0xD4, 55))
        purple_rad.setColorAt(0.5, QColor(0x77, 0x59, 0xD4, 20))
        purple_rad.setColorAt(1.0, QColor(0x77, 0x59, 0xD4, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(purple_rad))
        p.drawEllipse(QRectF(gx - 180, gy - 180, 360, 360))

        # Cyan glow — top-left area with smooth radial falloff
        gx2 = rect.left() + 50
        gy2 = rect.top() + rect.height() * 0.28
        cyan_rad = QRadialGradient(gx2, gy2, 180)
        cyan_rad.setColorAt(0.0, QColor(0x2C, 0xBF, 0xE3, 50))
        cyan_rad.setColorAt(0.5, QColor(0x2C, 0xBF, 0xE3, 18))
        cyan_rad.setColorAt(1.0, QColor(0x2C, 0xBF, 0xE3, 0))
        p.setBrush(QBrush(cyan_rad))
        p.drawEllipse(QRectF(gx2 - 180, gy2 - 180, 360, 360))

        p.setClipping(False)

        # ── outer border ──────────────────────────────────────────────────────
        p.setPen(QPen(C_BORDER, 1.0))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)
        p.end()
