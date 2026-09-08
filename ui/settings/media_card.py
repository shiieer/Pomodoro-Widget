from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.settings.cards import Card
from ui.settings.media_preview import MediaPreview


class MediaCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        card = Card("Image / GIF")
        hint = QLabel("Choose a file form your computer for each phase.")
        hint.setObjectName("Muted")
        card.add(hint)

        gifs = store.get("gifs", {})
        self.edits: dict[str, QLineEdit] = {}
        self.previews: dict[str, MediaPreview] = {}

        row = QHBoxLayout()
        row.setSpacing(12)
        row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        for key, label in (
            ("work", "Work"),
            ("short_break", "Short break"),
            ("long_break", "Long break"),
        ):
            row.addWidget(self._slot(label, key, gifs.get(key, "")))
        wrap = QWidget()
        wrap.setLayout(row)
        card.add(wrap)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        layout.addStretch()

    def _slot(self, label: str, key: str, value: str) -> QWidget:
        wrap = QWidget()
        wrap.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        column = QVBoxLayout(wrap)
        column.setContentsMargins(0, 0, 0, 0)
        column.setSpacing(8)
        title = QLabel(label)
        title.setObjectName("Muted")
        preview = MediaPreview(value)
        preview.path_changed.connect(lambda path, k=key: self._on_drop(k, path))
        edit = QLineEdit(value)
        edit.textChanged.connect(lambda text, p=preview: p.set_path(text.strip()))
        browse = QPushButton("Browse")
        browse.clicked.connect(lambda _, e=edit: self._browse(e))
        column.addWidget(title)
        column.addWidget(preview)
        column.addWidget(edit)
        column.addWidget(browse)
        self.edits[key] = edit
        self.previews[key] = preview
        return wrap

    def _on_drop(self, key: str, path: str) -> None:
        edit = self.edits[key]
        edit.blockSignals(True)
        edit.setText(path)
        edit.blockSignals(False)
        self.previews[key].set_path(path)

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
