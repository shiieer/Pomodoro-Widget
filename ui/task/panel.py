from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.common import DraggableMixin
from ui.icons import get_icon, get_pixmap
from ui.task.section import TaskSection
from ui.task.style import (
    C_ACCENT,
    C_DIM,
    C_MUTED,
    C_TEXT,
    TASK_QSS,
)
from ui.task.task_row import TaskRow

if TYPE_CHECKING:
    from core.task_store import TaskStore


class TaskPanel(DraggableMixin, QDialog):
    """
    Task manager dialog. Call `show()` / `exec()` from the main window.
    Emits `task_changed` whenever the list is mutated so callers can refresh TaskCard.
    """

    task_changed = pyqtSignal()

    def __init__(self, task_store: TaskStore, parent=None):
        super().__init__(parent)
        self._store = task_store

        self.setWindowTitle("Tasks")
        self.setModal(False)  # non-modal so timer keeps running
        self.resize(420, 560)
        self.setMinimumWidth(340)

        # Frameless rounded dialog
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(TASK_QSS)

        # Outer rounded container
        container = QFrame(self)
        container.setObjectName("TaskContainer")
        container.setStyleSheet(
            "QFrame#TaskContainer {"
            "  background: #151B27;"
            "  border: 1px solid rgba(255, 255, 255, 0.15);"
            "  border-radius: 18px;"
            "}"
        )

        # ── Header ────────────────────────────────────────────────────────────
        title_icon = QLabel()
        title_icon.setPixmap(
            get_pixmap("check", color=C_ACCENT, size=16, stroke_width=2.5)
        )
        title_lbl = QLabel("Tasks")
        title_lbl.setStyleSheet(
            f"color: {C_TEXT}; font-size: 16px; font-weight: 700; background: transparent;"
        )

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet(
            f"color: {C_DIM}; font-size: 12px; background: transparent;"
        )

        close_btn = QPushButton()
        close_btn.setObjectName("IconBtn")
        close_btn.setIcon(get_icon("x", color=C_MUTED, size=14, active_color="#FF8080"))
        close_btn.setIconSize(QSize(14, 14))
        close_btn.setFixedSize(28, 28)
        close_btn.setToolTip("Close Tasks")
        close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: rgba(255, 80, 80, 0.25); }"
        )
        close_btn.clicked.connect(self.close)

        hdr = QHBoxLayout()
        hdr.setContentsMargins(20, 16, 16, 8)
        hdr.setSpacing(8)
        hdr.addWidget(title_icon)
        hdr.addWidget(title_lbl)
        hdr.addWidget(self._count_lbl)
        hdr.addStretch()
        hdr.addWidget(close_btn)

        # ── Add-task row ──────────────────────────────────────────────────────
        self._input = QLineEdit()
        self._input.setPlaceholderText("Add a new task…")
        self._input.returnPressed.connect(self._add_task)

        add_btn = QPushButton("Add")
        add_btn.setIcon(get_icon("plus", color="#09212D", size=13, stroke_width=2.5))
        add_btn.setIconSize(QSize(13, 13))
        add_btn.setObjectName("AddBtn")
        add_btn.clicked.connect(self._add_task)

        input_row = QHBoxLayout()
        input_row.setContentsMargins(20, 0, 20, 0)
        input_row.setSpacing(10)
        input_row.addWidget(self._input, 1)
        input_row.addWidget(add_btn)

        # ── Scrollable task list area ─────────────────────────────────────────
        self._list_widget = QWidget()
        self._list_widget.setStyleSheet("background: transparent;")
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(20, 0, 20, 20)
        self._list_layout.setSpacing(12)
        self._list_layout.addStretch()

        scroll = QScrollArea()
        scroll.setWidget(self._list_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")

        # Container layout
        container_lay = QVBoxLayout(container)
        container_lay.setContentsMargins(0, 0, 0, 0)
        container_lay.setSpacing(12)
        container_lay.addLayout(hdr)
        container_lay.addLayout(input_row)
        container_lay.addWidget(scroll, 1)

        # Dialog root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(container)

        # ESC shortcut closes
        QShortcut(QKeySequence("Escape"), self, activated=self.close)

        self._refresh()

    # ── refresh ───────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        # Clear existing rows
        while self._list_layout.count() > 1:  # keep the trailing stretch
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks = self._store.all()
        todo = [t for t in tasks if not t.get("done")]
        done = [t for t in tasks if t.get("done")]

        # ── To do section ──────────────────────────────────────────────────
        if todo:
            todo_sec = TaskSection("To do")
            for t in todo:
                todo_sec.add_row(TaskRow(t, self._store, self._on_change))
            self._list_layout.insertWidget(self._list_layout.count() - 1, todo_sec)

        # ── Done section ───────────────────────────────────────────────────
        if done:
            done_sec = TaskSection("Done")
            for t in done:
                done_sec.add_row(TaskRow(t, self._store, self._on_change))

            # clear-done button at the bottom of the section
            clear_btn = QPushButton("Clear completed")
            clear_btn.setObjectName("DangerBtn")
            clear_btn.clicked.connect(self._clear_done)
            clear_wrap = QHBoxLayout()
            clear_wrap.setContentsMargins(12, 4, 12, 10)
            clear_wrap.addStretch()
            clear_wrap.addWidget(clear_btn)
            clear_w = QWidget()
            clear_w.setStyleSheet("background: transparent;")
            clear_w.setLayout(clear_wrap)
            done_sec.add_row(clear_w)

            self._list_layout.insertWidget(self._list_layout.count() - 1, done_sec)

        # ── empty state ────────────────────────────────────────────────────
        if not tasks:
            empty = QLabel("No tasks yet — add one above ✨")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                f"color: {C_DIM}; font-size: 13px; padding: 40px 0; background: transparent;"
            )
            self._list_layout.insertWidget(self._list_layout.count() - 1, empty)

        # ── count badge ────────────────────────────────────────────────────
        pending = self._store.pending_count()
        if pending:
            self._count_lbl.setText(f"{pending} pending")
        else:
            self._count_lbl.setText(
                f"{self._store.done_count()} done 🎉" if done else ""
            )

        self.task_changed.emit()

    # ── actions ───────────────────────────────────────────────────────────────

    def _add_task(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        self._store.add(text)
        self._input.clear()
        self._refresh()

    def _on_change(self) -> None:
        self._refresh()

    def _clear_done(self) -> None:
        self._store.clear_done()
        self._refresh()
