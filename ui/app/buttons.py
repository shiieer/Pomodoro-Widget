from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import QPushButton, QSizePolicy

from ui.app.constants import (
    C_ACCENT,
    C_ACCENT2,
    C_BTN_BG,
    C_BTN_BORDER,
    C_TEXT,
    app_font,
)
from ui.icons import get_pixmap


class GhostButton(QPushButton):
    def __init__(self, icon_name: str, label: str = "", parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._label = label
        self.setFixedHeight(48)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if label:
            self.setMinimumWidth(96)
        else:
            self.setFixedWidth(48)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 12.0

        p.setPen(QPen(C_BTN_BORDER, 1.0))
        p.setBrush(QBrush(C_BTN_BG))
        p.drawRoundedRect(rect, radius, radius)

        icon_size = 16
        pix = get_pixmap(self._icon_name, color="#F7FAFF", size=icon_size)

        if self._label:
            # Draw icon and label centered
            spacing = 8
            font = app_font(11, QFont.Weight.Medium)
            p.setFont(font)
            metrics = p.fontMetrics()
            text_w = metrics.horizontalAdvance(self._label)
            total_w = icon_size + spacing + text_w

            start_x = (self.width() - total_w) / 2
            icon_y = (self.height() - icon_size) / 2
            p.drawPixmap(int(start_x), int(icon_y), pix)

            text_rect = QRectF(start_x + icon_size + spacing, 0, text_w, self.height())
            p.setPen(C_TEXT)
            p.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self._label,
            )
        else:
            # Just icon centered
            ix = int((self.width() - icon_size) / 2)
            iy = int((self.height() - icon_size) / 2)
            p.drawPixmap(ix, iy, pix)

        p.end()


class PauseButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self.setFixedHeight(48)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def setRunning(self, running: bool) -> None:
        self._running = running
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        radius = 12.0

        # Glow shadow
        glow_rect = rect.adjusted(-2, 2, 2, 10)
        glow_grad = QLinearGradient(glow_rect.topLeft(), glow_rect.bottomLeft())
        glow_grad.setColorAt(0.0, QColor(0x38, 0xBD, 0xE8, 66))
        glow_grad.setColorAt(1.0, Qt.GlobalColor.transparent)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(glow_grad))
        p.drawRoundedRect(glow_rect, radius, radius)

        # Fill gradient
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, C_ACCENT)
        grad.setColorAt(1.0, C_ACCENT2)
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(rect, radius, radius)

        # Label & vector icon
        label_text = "Pause" if self._running else "Start"
        icon_name = "pause" if self._running else "play"
        icon_size = 15
        dark_teal = "#09212D"
        pix = get_pixmap(icon_name, color=dark_teal, size=icon_size)

        spacing = 8
        font = app_font(12, QFont.Weight.Bold)
        p.setFont(font)
        metrics = p.fontMetrics()
        text_w = metrics.horizontalAdvance(label_text)
        total_w = icon_size + spacing + text_w

        start_x = (self.width() - total_w) / 2
        icon_y = (self.height() - icon_size) / 2
        p.drawPixmap(int(start_x), int(icon_y), pix)

        text_rect = QRectF(start_x + icon_size + spacing, 0, text_w, self.height())
        p.setPen(QColor(0x09, 0x21, 0x2D))
        p.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            label_text,
        )

        p.end()
