from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QImageReader, QMovie, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QSizePolicy, QVBoxLayout

IMAGE_SUFFIXES = {".gif", ".png", ".jpg", ".jpeg", ".webp", ".bmp"}
PREVIEW_SIZE = 140
PADDING = 12
SLOT_SIZE = PREVIEW_SIZE + PADDING * 2


def first_image_path(event) -> str:
    mime = event.mimeData()
    if not mime.hasUrls():
        return ""
    for url in mime.urls():
        path = Path(url.toLocalFile())
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES:
            return str(path)
    return ""


class MediaPreview(QFrame):
    path_changed = pyqtSignal(str)

    def __init__(self, path: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("DropSlot")
        self.setAcceptDrops(True)
        self.setProperty("hover", False)
        self.preview_size = PREVIEW_SIZE
        self._movie: QMovie | None = None

        self.setFixedSize(SLOT_SIZE, SLOT_SIZE)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.image = QLabel()
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image.setFixedSize(PREVIEW_SIZE, PREVIEW_SIZE)
        self.image.setWordWrap(True)
        self.image.setObjectName("Muted")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)
        self.set_path(path)

    def set_path(self, path: str) -> None:
        self._stop_movie()
        self.image.clear()

        if not path or not Path(path).is_file():
            self.image.setText("Drop here")
            return

        reader = QImageReader(path)
        if reader.supportsAnimation():
            self._load_movie(path)
        else:
            self._load_image(path)

    def dragEnterEvent(self, event) -> None:
        if first_image_path(event):
            event.acceptProposedAction()
            self._set_hover(True)
        else:
            event.ignore()

    def dragLeaveEvent(self, event) -> None:
        self._set_hover(False)
        event.accept()

    def dropEvent(self, event) -> None:
        self._set_hover(False)
        path = first_image_path(event)
        if not path:
            event.ignore()
            return
        self.set_path(path)
        self.path_changed.emit(path)
        event.acceptProposedAction()

    def _set_hover(self, active: bool) -> None:
        self.setProperty("hover", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def _load_movie(self, path: str) -> None:
        movie = QMovie(path)
        if not movie.isValid():
            self._load_image(path)
            return
        movie.setScaledSize(QSize(self.preview_size, self.preview_size))
        self.image.setText("")
        self.image.setMovie(movie)
        movie.start()
        self._movie = movie

    def _load_image(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.image.setText("Drop here")
            return
        scaled = pixmap.scaled(
            self.preview_size,
            self.preview_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image.setText("")
        self.image.setPixmap(scaled)

    def _stop_movie(self) -> None:
        if self._movie is not None:
            self._movie.stop()
            self.image.setMovie(None)
            self._movie.deleteLater()
            self._movie = None
