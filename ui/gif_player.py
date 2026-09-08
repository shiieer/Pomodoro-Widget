from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QImageReader, QMovie, QPixmap
from PyQt6.QtWidgets import QLabel


class GifPlayer(QLabel):
    def __init__(self, size: int = 120, parent=None):
        super().__init__(parent)
        self.gif_size = size
        self._movie: QMovie | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def set_gif_size(self, size: int) -> None:
        self.gif_size = size
        self.setFixedSize(size, size)
        if self._movie is not None:
            self._movie.setScaledSize(QSize(size, size))
        elif not self.pixmap().isNull():
            self._show_pixmap(self.pixmap())

    def load(self, path: str) -> None:
        self._stop_movie()
        self.clear()

        if not path or not Path(path).is_file():
            return

        reader = QImageReader(path)
        if reader.supportsAnimation():
            self._load_movie(path)
        else:
            self._load_image(path)

    def _load_movie(self, path: str) -> None:
        movie = QMovie(path)
        if not movie.isValid():
            self._load_image(path)
            return
        movie.setScaledSize(QSize(self.gif_size, self.gif_size))
        self.setMovie(movie)
        movie.start()
        self._movie = movie

    def _load_image(self, path: str) -> None:
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return
        self._show_pixmap(pixmap)

    def _show_pixmap(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(
            self.gif_size,
            self.gif_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(scaled)

    def _stop_movie(self) -> None:
        if self._movie is not None:
            self._movie.stop()
            self.setMovie(None)
            self._movie.deleteLater()
            self._movie = None
