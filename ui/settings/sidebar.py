from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QListWidget, QListWidgetItem


class SettingsSidebar(QListWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(180)

        for name in ("Timer", "Look", "Media"):
            QListWidgetItem(name, self)

        self.setCurrentRow(0)
        self.currentRowChanged.connect(self.page_changed.emit)
