from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtWidgets import QListWidget, QListWidgetItem

from ui.icons import get_icon


class SettingsSidebar(QListWidget):
    page_changed = pyqtSignal(int)

    _ITEMS = (
        ("clock", "Timer"),
        ("palette", "Look"),
        ("image", "Media"),
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavList")
        self.setFixedWidth(160)
        self.setSpacing(2)
        self.setIconSize(QSize(16, 16))

        for icon_name, name in self._ITEMS:
            item = QListWidgetItem(f"  {name}", self)
            item.setIcon(
                get_icon(icon_name, color="#AEB8C9", size=16, active_color="#9EE7FF")
            )

        self.setCurrentRow(0)
        self.currentRowChanged.connect(self.page_changed.emit)
