from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.app.constants import (
    C_BTN_BORDER,
    C_DIM,
    C_GREEN,
    C_TASK_BG,
    C_TEXT,
    app_font,
)
from ui.icons import get_pixmap


class TaskCard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._task_name = "CURR TASK #1"
        self._streak = 3
        self.setFixedHeight(72)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def setTask(self, name: str, streak: int = 0) -> None:
        self._task_name = name
        self._streak = streak
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 18.0

        # Card bg
        p.setPen(QPen(C_BTN_BORDER, 1.0))
        p.setBrush(QBrush(C_TASK_BG))
        p.drawRoundedRect(rect, radius, radius)

        # Icon circle
        icon_r = 17.0
        icon_cx = rect.left() + 16 + icon_r
        icon_cy = rect.center().y()
        icon_rect = QRectF(icon_cx - icon_r, icon_cy - icon_r, icon_r * 2, icon_r * 2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(0x8C, 0xDE, 0xFF, 36)))
        p.drawEllipse(icon_rect)

        # Checkmark vector icon
        check_pix = get_pixmap("check", color="#9EE7FF", size=15, stroke_width=2.5)
        p.drawPixmap(int(icon_cx - 7.5), int(icon_cy - 7.5), check_pix)

        # Task text
        text_x = icon_cx + icon_r + 12
        p.setPen(C_TEXT)
        p.setFont(app_font(11, QFont.Weight.Medium))
        task_rect = QRectF(text_x, rect.top() + 8, rect.width() - text_x - 80, 26)
        p.drawText(task_rect, Qt.AlignmentFlag.AlignVCenter, self._task_name)

        # Muted sub-label
        p.setPen(C_DIM)
        p.setFont(app_font(9))
        sub_rect = QRectF(text_x, task_rect.bottom(), task_rect.width(), 22)
        p.drawText(sub_rect, Qt.AlignmentFlag.AlignVCenter, "Current Focus")

        # Streak badge (right side)
        badge_w = 64.0
        badge_rect = QRectF(
            rect.right() - badge_w - 12, rect.center().y() - 16, badge_w, 32
        )
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(0x9B, 0xE8, 0xB8, 30)))
        p.drawRoundedRect(badge_rect, 8, 8)

        # Draw flame icon + streak number
        flame_pix = get_pixmap("flame", color="#9BE8B8", size=14)
        streak_num = str(self._streak)
        p.setFont(app_font(10, QFont.Weight.Bold))
        metrics = p.fontMetrics()
        num_w = metrics.horizontalAdvance(streak_num)
        total_w = 14 + 5 + num_w
        start_x = badge_rect.center().x() - total_w / 2
        flame_y = badge_rect.center().y() - 7

        p.drawPixmap(int(start_x), int(flame_y), flame_pix)
        p.setPen(C_GREEN)
        num_rect = QRectF(
            start_x + 19, badge_rect.top(), num_w + 4, badge_rect.height()
        )
        p.drawText(
            num_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            streak_num,
        )

        p.end()
