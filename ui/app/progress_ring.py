from __future__ import annotations

import math

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget

from ui.app.constants import C_ACCENT, C_MUTED, C_TEXT, app_font


class ArcProgressRing(QWidget):
    RING_W = 8
    TRACK_W = 8
    SIZE = 228

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 0.0  # 0 → 1 (fraction elapsed)
        self._time_text = "25:00"
        self._sub_text = "Session"
        self._session_num = ""
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def setState(
        self, time_text: str, sub_text: str, session_num: str, progress: float
    ) -> None:
        self._time_text = time_text
        self._sub_text = sub_text
        self._session_num = session_num
        self._progress = max(0.0, min(1.0, progress))
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height())
        margin = self.RING_W + 2
        ring_rect = QRectF(margin, margin, side - 2 * margin, side - 2 * margin)

        # ── track ring (faint white) ──────────────────────────────────────────
        p.setPen(
            QPen(
                QColor(255, 255, 255, 18),
                self.TRACK_W,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(ring_rect)

        # ── progress arc (cyan glow) ──────────────────────────────────────────
        if self._progress > 0.001:
            span_deg = int(self._progress * 360 * 16)
            start_angle = 90 * 16

            # Glow: wider, semi-transparent
            glow_pen = QPen(
                QColor(0x9E, 0xE7, 0xFF, 64),
                self.RING_W + 8,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
            p.setPen(glow_pen)
            p.drawArc(ring_rect, start_angle, -span_deg)

            # Main arc
            arc_pen = QPen(
                C_ACCENT, self.RING_W, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap
            )
            p.setPen(arc_pen)
            p.drawArc(ring_rect, start_angle, -span_deg)

            # Glowing dot at the arc tip
            angle_rad = math.radians(90 - self._progress * 360)
            cx = ring_rect.center().x() + ring_rect.width() / 2 * math.cos(angle_rad)
            cy = ring_rect.center().y() - ring_rect.height() / 2 * math.sin(angle_rad)
            p.setPen(Qt.PenStyle.NoPen)
            # outer glow
            p.setBrush(QBrush(QColor(0x9E, 0xE7, 0xFF, 90)))
            p.drawEllipse(QRectF(cx - 7, cy - 7, 14, 14))
            # dot
            p.setBrush(QBrush(C_ACCENT))
            p.drawEllipse(QRectF(cx - 3, cy - 3, 6, 6))

        # ── timer text ────────────────────────────────────────────────────────
        center = ring_rect.center()

        # Big time
        p.setPen(C_TEXT)
        p.setFont(app_font(42, QFont.Weight.Bold))
        time_rect = QRectF(0, center.y() - 50, self.width(), 56)
        p.drawText(time_rect, Qt.AlignmentFlag.AlignCenter, self._time_text)

        # Sub label
        p.setPen(C_MUTED)
        p.setFont(app_font(9, QFont.Weight.Normal))
        sub_rect = QRectF(0, center.y() + 12, self.width(), 22)
        p.drawText(sub_rect, Qt.AlignmentFlag.AlignCenter, self._sub_text)

        p.end()
