from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt6.QtWidgets import QApplication, QWidget

# ── dimensions ────────────────────────────────────────────────────────────────
_BODY_W = 70  # width  of top/bottom tabs (horizontal)
_BODY_H = 50  # height of top/bottom tabs (vertical)
_LR_W = 76  # width  of left/right tabs — room for text + chevrons side by side
_LR_H = 60  # height of left/right tabs (tall enough for rotated text)
_RADIUS = 10.0  # corner radius

_PULSE_MS = 900


def _font(size: int, weight: QFont.Weight = QFont.Weight.Bold) -> QFont:
    return QFont("Segoe UI", size, int(weight))


class PeekTab(QWidget):
    def __init__(self, on_click: Callable[[], None], parent=None):
        super().__init__(parent)
        self._on_click = on_click
        self._time_text = "00:00"
        self._edge = "bottom"
        self._glow: float = 1.0
        self._glow_dir: int = -1

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._update_size()

        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(16)
        self._pulse_timer.timeout.connect(self._tick_glow)

        self._anim = QPropertyAnimation(self, b"pos", self)
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # ── public API ────────────────────────────────────────────────────────────

    def show_at(
        self, edge: str, mini_pos: QPoint, mini_w: int, mini_h: int, time_text: str
    ) -> None:
        self._edge = edge
        self._time_text = time_text
        self._update_size()

        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        tw, th = self.width(), self.height()

        if edge == "bottom":
            cx = mini_pos.x() + mini_w // 2
            x = cx - tw // 2
            y = geo.bottom() - th + 1
        elif edge == "top":
            cx = mini_pos.x() + mini_w // 2
            x = cx - tw // 2
            y = geo.top()
        elif edge == "left":
            cy = mini_pos.y() + mini_h // 2
            x = geo.left()
            y = cy - th // 2
        else:  # right
            cy = mini_pos.y() + mini_h // 2
            x = geo.right() - tw + 1
            y = cy - th // 2

        x = max(geo.left(), min(x, geo.right() - tw))
        y = max(geo.top(), min(y, geo.bottom() - th))
        end = QPoint(x, y)

        # start slightly off-screen
        if edge == "bottom":
            start = QPoint(x, geo.bottom() + 6)
        elif edge == "top":
            start = QPoint(x, geo.top() - th - 6)
        elif edge == "left":
            start = QPoint(geo.left() - tw - 6, y)
        else:
            start = QPoint(geo.right() + 6, y)

        self.move(start)
        self.show()
        self.raise_()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

        self._glow = 1.0
        self._glow_dir = -1
        self._pulse_timer.start()

    def update_time(self, time_text: str) -> None:
        if self._time_text != time_text:
            self._time_text = time_text
            self.update()

    def hide_tab(self) -> None:
        self._pulse_timer.stop()
        self.hide()

    # ── sizing ────────────────────────────────────────────────────────────────

    def _update_size(self) -> None:
        if self._edge in ("top", "bottom"):
            self.setFixedSize(_BODY_W, _BODY_H)
        else:
            self.setFixedSize(_LR_W, _LR_H)

    # ── pulse ─────────────────────────────────────────────────────────────────

    def _tick_glow(self) -> None:
        step = 16 / _PULSE_MS
        self._glow += self._glow_dir * step * 2
        if self._glow <= 0.3:
            self._glow, self._glow_dir = 0.3, +1
        elif self._glow >= 1.0:
            self._glow, self._glow_dir = 1.0, -1
        self.update()

    # ── mouse ─────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mousePressEvent(event)

    # ── paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        edge = self._edge

        bg_a = int(210 + self._glow * 35)  # 210–245 pulsing grey
        bg = QColor(bg_a, bg_a, bg_a, 250)
        ink = QColor(0x0A, 0x0A, 0x0A)

        # Build the combined body+pointer path
        shape = self._make_shape(w, h, edge)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bg))
        p.drawPath(shape)

        # Draw content (time + chevrons) inside the body rect
        body_rect = self._body_rect(w, h, edge)
        self._draw_content(p, body_rect, edge, ink)

        p.end()

    # ── shape construction ────────────────────────────────────────────────────

    def _body_rect(self, w: int, h: int, edge: str) -> QRectF:
        return QRectF(0, 0, w, h)

    def _make_shape(self, w: int, h: int, edge: str) -> QPainterPath:
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, w, h), _RADIUS, _RADIUS)
        return path

    # ── content drawing ───────────────────────────────────────────────────────

    def _draw_content(self, p: QPainter, body: QRectF, edge: str, ink: QColor) -> None:
        """Draw time text + double chevrons inside the body rect."""
        bw, bh = body.width(), body.height()
        bx, by = body.x(), body.y()

        if edge == "bottom":
            # chevrons at top of body, time below
            chev_cy = by + bh * 0.36
            self._draw_double_chevron(p, bx + bw / 2, chev_cy, "up", ink)
            p.setPen(ink)
            p.setFont(_font(14))
            p.drawText(
                QRectF(bx, by + bh * 0.52, bw, bh * 0.44),
                Qt.AlignmentFlag.AlignCenter,
                self._time_text,
            )

        elif edge == "top":
            # upside-down: time at top, chevrons below pointing down
            p.save()
            p.translate(bx + bw / 2, by + bh / 2)
            p.rotate(180)
            self._draw_double_chevron(p, 0, bh * 0.20, "up", ink)
            p.setPen(ink)
            p.setFont(_font(14))
            p.drawText(
                QRectF(-bw / 2, -bh * 0.48, bw, bh * 0.44),
                Qt.AlignmentFlag.AlignCenter,
                self._time_text,
            )
            p.restore()

        elif edge == "left":
            # left tab: [time CCW | »chevron] side by side
            half = bw / 2
            pad = 6.0

            # time in left half, rotated 90° CCW
            p.save()
            p.translate(bx + half / 2, by + bh / 2)
            p.rotate(-90)
            p.setPen(ink)
            p.setFont(_font(13))
            p.drawText(
                QRectF(-bh / 2 + pad, -10, bh - pad * 2, 20),
                Qt.AlignmentFlag.AlignCenter,
                self._time_text,
            )
            p.restore()

            # chevrons pointing right in right half
            self._draw_double_chevron(
                p, bx + half + half / 2, by + bh / 2, "right", ink
            )

        else:  # right
            # right tab: [«chevron | time CW] side by side
            half = bw / 2
            pad = 6.0

            # chevrons pointing left in left half
            self._draw_double_chevron(p, bx + half / 2, by + bh / 2, "left", ink)

            # time in right half, rotated 90° CW
            p.save()
            p.translate(bx + half + half / 2, by + bh / 2)
            p.rotate(90)
            p.setPen(ink)
            p.setFont(_font(13))
            p.drawText(
                QRectF(-bh / 2 + pad, -10, bh - pad * 2, 20),
                Qt.AlignmentFlag.AlignCenter,
                self._time_text,
            )
            p.restore()

    def _draw_double_chevron(
        self,
        p: QPainter,
        cx: float,
        cy: float,
        direction: str,
        ink: QColor,
        s: float = 7.0,
        gap: float = 7.0,
    ) -> None:
        """Two stacked open chevrons pointing in `direction`."""
        pen = QPen(
            ink,
            2.3,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap,
            Qt.PenJoinStyle.RoundJoin,
        )
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)

        for i, offset in enumerate((0.0, gap)):
            path = QPainterPath()
            if direction == "up":
                y0 = cy + (gap / 2) - i * gap
                path.moveTo(cx - s, y0 + s * 0.65)
                path.lineTo(cx, y0)
                path.lineTo(cx + s, y0 + s * 0.65)
            elif direction == "down":
                y0 = cy - (gap / 2) + i * gap
                path.moveTo(cx - s, y0 - s * 0.65)
                path.lineTo(cx, y0)
                path.lineTo(cx + s, y0 - s * 0.65)
            elif direction == "right":
                x0 = cx - (gap / 2) + i * gap
                path.moveTo(x0 - s * 0.65, cy - s)
                path.lineTo(x0, cy)
                path.lineTo(x0 - s * 0.65, cy + s)
            elif direction == "left":
                x0 = cx + (gap / 2) - i * gap
                path.moveTo(x0 + s * 0.65, cy - s)
                path.lineTo(x0, cy)
                path.lineTo(x0 + s * 0.65, cy + s)
            p.drawPath(path)
