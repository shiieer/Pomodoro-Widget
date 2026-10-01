from __future__ import annotations

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from ui.app.constants import app_font
from ui.icons import get_icon, get_pixmap


class HeaderIcon(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(0, 0, 24, 24)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(0x8C, 0xDE, 0xFF, 36)))
        p.drawRoundedRect(rect, 7, 7)

        # Draw crisp clock vector icon
        pix = get_pixmap("clock", color="#9EE7FF", size=14, stroke_width=2.2)
        p.drawPixmap(5, 5, pix)
        p.end()


class HeaderBar(QWidget):
    def __init__(
        self,
        on_settings_clicked,
        on_close_clicked=None,
        on_minimize_clicked=None,
        parent=None,
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        icon = HeaderIcon()
        title = QLabel("FocusTimer")
        title.setFont(app_font(11, QFont.Weight.Medium))
        title.setStyleSheet("color: #F7FAFF; background: transparent;")

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setIcon(
            get_icon("settings", color="#AEB8C9", size=15, active_color="#F7FAFF")
        )
        self.settings_btn.setIconSize(QSize(15, 15))
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.08); }"
        )
        self.settings_btn.clicked.connect(on_settings_clicked)

        # Switch to mini widget button
        self.min_btn = QPushButton()
        self.min_btn.setIcon(
            get_icon("minimize-2", color="#AEB8C9", size=14, active_color="#9EE7FF")
        )
        self.min_btn.setIconSize(QSize(14, 14))
        self.min_btn.setFixedSize(28, 28)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.setToolTip("Switch to Mini Widget")
        self.min_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.08); }"
        )
        if on_minimize_clicked:
            self.min_btn.clicked.connect(on_minimize_clicked)

        # Close app button
        self.close_btn = QPushButton()
        self.close_btn.setIcon(
            get_icon("x", color="#AEB8C9", size=14, active_color="#FF8080")
        )
        self.close_btn.setIconSize(QSize(14, 14))
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Close FocusTimer")
        self.close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255, 80, 80, 0.25); }"
        )
        self.close_btn.clicked.connect(on_close_clicked or QApplication.quit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(6)
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.settings_btn)
        if on_minimize_clicked:
            layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
