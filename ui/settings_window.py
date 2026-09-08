from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.settings.look_card import LookCard
from ui.settings.media_card import MediaCard
from ui.settings.sidebar import SettingsSidebar
from ui.settings.style import SETTINGS_QSS
from ui.settings.timer_card import TimerCard


class SettingsWindow(QDialog):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store
        self.setWindowTitle("Pomodoro Settings")
        self.setModal(True)
        self.resize(920, 620)
        self.setStyleSheet(SETTINGS_QSS)

        root = QWidget()
        root.setObjectName("Root")

        self.sidebar = SettingsSidebar()
        self.timer_card = TimerCard(store)
        self.look_card = LookCard(store)
        self.media_card = MediaCard(store)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.timer_card)
        self.pages.addWidget(self.look_card)
        self.pages.addWidget(self.media_card)
        self.sidebar.page_changed.connect(self.pages.setCurrentIndex)

        body = QHBoxLayout()
        body.setContentsMargins(16, 16, 16, 8)
        body.setSpacing(16)
        body.addWidget(self.sidebar)
        body.addWidget(self.pages, 1)

        save = QPushButton("Save")
        save.setObjectName("Accent")
        save.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        actions = QHBoxLayout()
        actions.setContentsMargins(16, 0, 16, 16)
        actions.addStretch()
        actions.addWidget(cancel)
        actions.addWidget(save)

        column = QVBoxLayout(root)
        column.setContentsMargins(0, 0, 0, 0)
        column.addLayout(body, 1)
        column.addLayout(actions)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(root)

    def values(self) -> dict:
        data = {}
        data.update(self.timer_card.values())
        data.update(self.look_card.values())
        data.update(self.media_card.values())
        return data
