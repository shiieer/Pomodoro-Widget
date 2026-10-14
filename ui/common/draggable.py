from __future__ import annotations

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QApplication


class DraggableMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._dragging = False
        self._drag_offset = QPoint()
        self._has_moved_manually = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self._has_moved_manually = True
            target = event.globalPosition().toPoint() - self._drag_offset
            screen = QApplication.screenAt(event.globalPosition().toPoint())
            if screen is None:
                screen = self.screen() or QApplication.primaryScreen()
            if screen is not None:
                bounds = screen.availableGeometry()
                frame = self.frameGeometry()
                target.setX(
                    max(
                        bounds.left(),
                        min(target.x(), bounds.right() - frame.width() + 1),
                    )
                )
                target.setY(
                    max(
                        bounds.top(),
                        min(target.y(), bounds.bottom() - frame.height() + 1),
                    )
                )
            self.move(target)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
        super().mouseReleaseEvent(event)
