from __future__ import annotations

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.common import DraggableMixin, HDivider
from ui.icons import get_icon, get_pixmap
from ui.settings.look_card import LookCard
from ui.settings.media_card import MediaCard
from ui.settings.sidebar import SettingsSidebar
from ui.settings.style import SETTINGS_QSS
from ui.settings.timer_card import TimerCard

# ── Header bar (matches the SVG top strip) ────────────────────────────────────


class _HeaderBar(QWidget):
    def __init__(self, on_close=None, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet("background: transparent;")

        # App icon — vector clock on tinted rounded square
        icon_lbl = QLabel()
        icon_lbl.setFixedSize(24, 24)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            "background: rgba(140,222,255,0.13); border-radius: 7px;"
        )
        icon_lbl.setPixmap(get_pixmap("clock", color="#9EE7FF", size=14))

        title_lbl = QLabel("FocusTimer")
        title_lbl.setStyleSheet(
            "color: #F7FAFF; font-size: 13px; font-weight: 500;"
            " background: transparent;"
        )

        gear_btn = QPushButton()
        gear_btn.setIcon(
            get_icon("settings", color="#AEB8C9", size=16, active_color="#F7FAFF")
        )
        gear_btn.setIconSize(QSize(16, 16))
        gear_btn.setFixedSize(28, 28)
        gear_btn.setObjectName("Ghost")
        gear_btn.setToolTip("Settings")
        gear_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255,255,255,0.08); }"
        )

        close_btn = QPushButton()
        close_btn.setIcon(
            get_icon("x", color="#AEB8C9", size=14, active_color="#FF8080")
        )
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("Close Settings")
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255, 80, 80, 0.25); }"
        )
        if on_close:
            close_btn.clicked.connect(on_close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)
        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addStretch()
        layout.addWidget(gear_btn)
        layout.addWidget(close_btn)


# ── Accent save button (cyan gradient) ───────────────────────────────────────


class _SaveButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Save & apply")
        self.setIcon(get_icon("check", color="#09212D", size=15, stroke_width=2.5))
        self.setIconSize(QSize(15, 15))
        self.setFixedHeight(42)
        self.setMinimumWidth(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("Accent")


# ── SettingsWindow ────────────────────────────────────────────────────────────


class SettingsWindow(DraggableMixin, QDialog):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        self.store = store

        self.setWindowTitle("FocusTimer — Settings")
        self.setModal(True)
        self.resize(860, 640)
        self.setMinimumSize(720, 520)

        # Frameless rounded window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(SETTINGS_QSS)

        # ── pages ─────────────────────────────────────────────────────────────
        self.timer_card = TimerCard(store)
        self.look_card = LookCard(store)
        self.media_card = MediaCard(store)

        self.pages = QStackedWidget()
        self.pages.addWidget(self.timer_card)
        self.pages.addWidget(self.look_card)
        self.pages.addWidget(self.media_card)

        # ── sidebar ────────────────────────────────────────────────────────────
        self.sidebar = SettingsSidebar()
        self.sidebar.page_changed.connect(self.pages.setCurrentIndex)

        # ── page title area ────────────────────────────────────────────────────
        self._page_title = QLabel("Timer")
        self._page_title.setObjectName("PageTitle")

        self._page_desc = QLabel("Set work and break durations for the widget")
        self._page_desc.setObjectName("AppDesc")

        self.sidebar.page_changed.connect(self._update_page_title)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)
        title_col.addWidget(self._page_title)
        title_col.addWidget(self._page_desc)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 12, 0, 12)
        title_row.addLayout(title_col)

        # ── body (sidebar + pages) ─────────────────────────────────────────────
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(20)
        body.addWidget(self.sidebar)
        body.addWidget(self.pages, 1)

        # ── footer buttons ─────────────────────────────────────────────────────
        restore_btn = QPushButton("Restore defaults")
        restore_btn.setIcon(get_icon("rotate-ccw", color="#AEB8C9", size=14))
        restore_btn.setIconSize(QSize(14, 14))
        restore_btn.setObjectName("Ghost")
        restore_btn.clicked.connect(self._restore_defaults)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        save_btn = _SaveButton()
        save_btn.clicked.connect(self.accept)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 8, 0, 0)
        footer.addWidget(restore_btn)
        footer.addStretch()
        footer.addWidget(cancel_btn)
        footer.addSpacing(8)
        footer.addWidget(save_btn)

        # ── container frame with rounded border ────────────────────────────────
        container = QFrame(self)
        container.setObjectName("SettingsContainer")
        container.setStyleSheet(
            "QFrame#SettingsContainer {"
            "  background: #151B27;"
            "  border: 1px solid rgba(255, 255, 255, 0.15);"
            "  border-radius: 20px;"
            "}"
        )

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(20, 0, 20, 16)
        content_lay.setSpacing(0)
        content_lay.addLayout(title_row)
        content_lay.addWidget(HDivider())
        content_lay.addSpacing(16)
        content_lay.addLayout(body, 1)
        content_lay.addLayout(footer)

        container_lay = QVBoxLayout(container)
        container_lay.setContentsMargins(0, 0, 0, 0)
        container_lay.setSpacing(0)
        container_lay.addWidget(_HeaderBar(on_close=self.reject))
        container_lay.addWidget(HDivider())
        container_lay.addWidget(content, 1)

        # Root layout for dialog
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(container)

    # ── internals ─────────────────────────────────────────────────────────────

    _PAGE_META = (
        ("Timer", "Set work and break durations for the widget"),
        ("Look", "Customize the widget's appearance and position"),
        ("Media", "Assign images or GIFs to each session phase"),
    )

    def _update_page_title(self, index: int) -> None:
        title, desc = self._PAGE_META[index]
        self._page_title.setText(title)
        self._page_desc.setText(desc)

    def _restore_defaults(self) -> None:
        self.timer_card.reset()
        self.look_card.reset()

    # ── public API ─────────────────────────────────────────────────────────────

    def values(self) -> dict:
        data: dict = {}
        data.update(self.timer_card.values())
        data.update(self.look_card.values())
        data.update(self.media_card.values())
        return data
