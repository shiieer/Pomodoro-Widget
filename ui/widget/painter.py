from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen

from core.timer import Phase
from ui.widget.constants import C_ACCENT, C_BG, C_BORDER, C_GREEN


def paint_mini_widget(widget, phase: Phase, remaining: int, total_seconds: int) -> None:
    RADIUS = 18
    p = QPainter(widget)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    rect = QRectF(widget.rect()).adjusted(1, 1, -1, -1)
    path = QPainterPath()
    path.addRoundedRect(rect, RADIUS, RADIUS)

    p.setClipPath(path)
    p.fillPath(path, QBrush(C_BG))

    grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
    grad.setColorAt(0.0, QColor(255, 255, 255, 12))
    grad.setColorAt(1.0, QColor(0, 0, 0, 40))
    p.fillPath(path, QBrush(grad))

    glow_color = (
        QColor(0x2C, 0xBF, 0xE3, 50)
        if phase == Phase.WORK
        else QColor(0x77, 0x59, 0xD4, 50)
    )
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(glow_color))
    p.drawEllipse(QRectF(rect.left() - 20, rect.top() - 20, 90, 90))

    progress = max(0.0, min(1.0, 1.0 - (remaining / max(1, total_seconds))))
    if progress > 0.001:
        bar_h = 3.0
        bar_y = rect.bottom() - bar_h
        bar_w = rect.width() * progress
        bar_rect = QRectF(rect.left(), bar_y, bar_w, bar_h)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(C_ACCENT if phase == Phase.WORK else C_GREEN))
        p.drawRoundedRect(bar_rect, 1.5, 1.5)

    p.setClipping(False)
    p.setPen(QPen(C_BORDER, 1.0))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawPath(path)
    p.end()
