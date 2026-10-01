from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton


class MiniButton(QPushButton):
    def __init__(self, icon: QIcon | None = None, tooltip: str = "", parent=None):
        super().__init__(parent)
        self.setFixedSize(26, 26)
        self.setIconSize(QSize(13, 13))
        if icon:
            self.setIcon(icon)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if tooltip:
            self.setToolTip(tooltip)
        self.setStyleSheet(
            "QPushButton {"
            "  background: rgba(255, 255, 255, 0.08);"
            "  border: 1px solid rgba(255, 255, 255, 0.12);"
            "  border-radius: 13px;"
            "  padding: 0px;"
            "}"
            "QPushButton:hover {"
            "  background: rgba(158, 231, 255, 0.22);"
            "  border: 1px solid rgba(158, 231, 255, 0.45);"
            "}"
            "QPushButton:pressed {"
            "  background: rgba(80, 200, 243, 0.35);"
            "}"
        )
