from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.icons import get_icon
from ui.settings.cards import RowItem, ScrollPage, SectionCard
from ui.settings.media_preview import MediaPreview


class MediaCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        gifs = store.get("gifs", {})

        self.edits: dict[str, QLineEdit] = {}
        self.previews: dict[str, MediaPreview] = {}

        # ── path rows card ────────────────────────────────────────────────────
        path_card = SectionCard("Media")

        for key, glyph, title, sub in (
            ("work", "⏱", "Work phase", "Image shown during focus"),
            ("short_break", "☕", "Short break", "Image shown during short breaks"),
            ("long_break", "🌙", "Long break", "Image shown during long break"),
        ):
            value = gifs.get(key, "")
            control = self._path_control(key, value)
            path_card.add_row(RowItem(glyph, title, sub, control))

        # ── preview area card ─────────────────────────────────────────────────
        preview_card = SectionCard("Preview")
        prev_row = QHBoxLayout()
        prev_row.setContentsMargins(16, 12, 16, 12)
        prev_row.setSpacing(16)
        prev_row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        for key, label in (
            ("work", "Work"),
            ("short_break", "Short"),
            ("long_break", "Long"),
        ):
            value = gifs.get(key, "")
            col = QVBoxLayout()
            col.setSpacing(4)

            lbl = QLabel(label)
            lbl.setStyleSheet(
                "color: #7B879A; font-size: 11px; background: transparent;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            preview = MediaPreview(value)
            preview.path_changed.connect(lambda path, k=key: self._on_drop(k, path))
            self.previews[key] = preview

            col.addWidget(preview)
            col.addWidget(lbl)
            prev_row.addLayout(col)

        prev_wrap = QWidget()
        prev_wrap.setStyleSheet("background: transparent;")
        prev_wrap.setLayout(prev_row)
        preview_card.add(prev_wrap)

        # ── page layout ───────────────────────────────────────────────────────
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)
        lay.addWidget(path_card)
        lay.addWidget(preview_card)
        lay.addStretch()

        page = ScrollPage(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _path_control(self, key: str, value: str) -> QWidget:
        edit = QLineEdit(value)
        edit.setPlaceholderText("No file")
        edit.setFixedWidth(170)
        edit.textChanged.connect(
            lambda text, k=key: self._sync_preview(k, text.strip())
        )

        browse = QPushButton("Browse")
        browse.setFixedWidth(68)
        browse.clicked.connect(lambda _, e=edit: self._browse(e))

        clear = QPushButton()
        clear.setIcon(get_icon("x", color="#7B879A", size=12, active_color="#FF8080"))
        clear.setIconSize(QSize(12, 12))
        clear.setFixedWidth(28)
        clear.setToolTip("Clear")
        clear.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 4px; padding: 0; }"
            "QPushButton:hover { background: rgba(255, 255, 255, 0.08); }"
        )
        clear.clicked.connect(lambda _, e=edit: e.clear())

        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lay.addWidget(edit)
        lay.addWidget(browse)
        lay.addWidget(clear)

        self.edits[key] = edit
        return wrap

    def _sync_preview(self, key: str, path: str) -> None:
        if key in self.previews:
            self.previews[key].set_path(path)

    def _on_drop(self, key: str, path: str) -> None:
        edit = self.edits[key]
        edit.blockSignals(True)
        edit.setText(path)
        edit.blockSignals(False)
        self._sync_preview(key, path)

    def _browse(self, edit: QLineEdit) -> None:
        start = edit.text().strip()
        directory = str(Path(start).parent) if start else ""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose image or GIF",
            directory,
            "Images (*.gif *.png *.jpg *.jpeg *.webp *.bmp);;All files (*.*)",
        )
        if path:
            edit.setText(path)

    def values(self) -> dict:
        return {"gifs": {key: edit.text().strip() for key, edit in self.edits.items()}}
