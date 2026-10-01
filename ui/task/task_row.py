from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from ui.icons import get_icon
from ui.task.style import (
    C_ACCENT,
    C_ACTIVE_BG,
    C_DIM,
    C_DONE_BG,
    C_GREEN,
    C_MUTED,
    C_TEXT,
)

if TYPE_CHECKING:
    from core.task_store import TaskStore


class TaskRow(QWidget):
    def __init__(
        self,
        task: dict,
        store: TaskStore,
        on_change: Callable[[], None],
        parent=None,
    ):
        super().__init__(parent)
        self._task = task
        self._store = store
        self._on_change = on_change

        is_done = task.get("done", False)
        is_active = task.get("active", False)

        # Background tint
        if is_done:
            self.setStyleSheet(f"background: {C_DONE_BG}; border-radius: 0px;")
        elif is_active:
            self.setStyleSheet(f"background: {C_ACTIVE_BG}; border-radius: 0px;")

        # ── Done toggle button ──────────────────────────────────────────────
        check_btn = QPushButton()
        check_btn.setObjectName("IconBtn")
        check_btn.setToolTip("Mark as done / undone")
        check_btn.setFixedSize(26, 26)
        check_btn.setIconSize(QSize(15, 15))
        if is_done:
            check_btn.setIcon(get_icon("check-circle", color=C_GREEN, size=15))
        elif is_active:
            check_btn.setIcon(get_icon("target", color=C_ACCENT, size=15))
        else:
            check_btn.setIcon(get_icon("circle", color=C_MUTED, size=15))
        check_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
        )
        check_btn.clicked.connect(self._toggle_done)

        # ── Title label ─────────────────────────────────────────────────────
        title = task.get("title", "")
        title_lbl = QLabel(title)
        title_lbl.setWordWrap(True)
        if is_done:
            title_lbl.setStyleSheet(
                f"color: {C_DIM}; text-decoration: line-through;"
                " font-size: 13px; background: transparent;"
            )
        elif is_active:
            title_lbl.setStyleSheet(
                f"color: {C_TEXT}; font-size: 13px; font-weight: 600;"
                " background: transparent;"
            )
        else:
            title_lbl.setStyleSheet(
                f"color: {C_MUTED}; font-size: 13px; background: transparent;"
            )

        # ── Set active button (only for pending, non-active tasks) ──────────
        if not is_done and not is_active:
            active_btn = QPushButton()
            active_btn.setObjectName("IconBtn")
            active_btn.setFixedSize(26, 26)
            active_btn.setIconSize(QSize(12, 12))
            active_btn.setIcon(get_icon("play", color=C_ACCENT, size=12))
            active_btn.setToolTip("Set as current focus task")
            active_btn.setStyleSheet(
                "QPushButton { background: transparent; border: none; }"
                "QPushButton:hover { background: rgba(255,255,255,0.08); border-radius: 4px; }"
            )
            active_btn.clicked.connect(self._set_active)
        else:
            active_btn = None

        # ── Delete button ────────────────────────────────────────────────────
        del_btn = QPushButton()
        del_btn.setObjectName("IconBtn")
        del_btn.setFixedSize(26, 26)
        del_btn.setIconSize(QSize(12, 12))
        del_btn.setIcon(get_icon("x", color=C_DIM, size=12, active_color="#FF8080"))
        del_btn.setToolTip("Delete task")
        del_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            "QPushButton:hover { background: rgba(255,255,255,0.08); border-radius: 4px; }"
        )
        del_btn.clicked.connect(self._delete)

        # ── Layout ──────────────────────────────────────────────────────────
        row = QHBoxLayout(self)
        row.setContentsMargins(12, 8, 12, 8)
        row.setSpacing(8)
        row.addWidget(check_btn)
        row.addWidget(title_lbl, 1)
        if active_btn:
            row.addWidget(active_btn)
        row.addWidget(del_btn)

    def _toggle_done(self) -> None:
        self._store.toggle_done(self._task["id"])
        self._on_change()

    def _set_active(self) -> None:
        self._store.set_active(self._task["id"])
        self._on_change()

    def _delete(self) -> None:
        self._store.delete(self._task["id"])
        self._on_change()
