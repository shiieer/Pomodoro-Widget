from pathlib import Path

from PyQt6.QtCore import QPoint, Qt, QTimer
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import QApplication, QLabel, QMenu, QVBoxLayout, QWidget

from config import GIF_DIR
from core.settings_store import SettingsStore
from core.timer import Phase, PomodoroTimer
from ui.gif_player import GifPlayer
from ui.settings_window import SettingsWindow

PHASE_LABELS = {
    Phase.WORK: "FOCUS",
    Phase.SHORT_BREAK: "BREAK",
    Phase.LONG_BREAK: "LONG BREAK",
}


class PomodoroWidget(QWidget):
    def __init__(self, store: SettingsStore):
        super().__init__()
        self.store = store
        self._drag_offset = QPoint()
        self._dragging = False
        self.settings_dialog: SettingsWindow | None = None

        self.setWindowTitle("Pomodoro")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.card = QWidget(self)
        self.gif = GifPlayer(store.get("gif_size"), self.card)
        self.phase_label = QLabel(self.card)
        self.time_label = QLabel(self.card)
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self.card)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(4)
        layout.addWidget(self.gif, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.phase_label)
        layout.addWidget(self.time_label)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

        self.timer = PomodoroTimer(
            work_seconds=store.get("work_minutes") * 60,
            short_break_seconds=store.get("short_break_minutes") * 60,
            long_break_seconds=store.get("long_break_minutes") * 60,
            session_until_long_break=store.get("sessions_until_long_break"),
            on_tick=self._on_tick,
            on_phase_change=self._on_phase_change,
        )

        self.clock = QTimer(self)
        self.clock.setInterval(1000)
        self.clock.timeout.connect(self.timer.tick)
        self.clock.start()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        self._apply_look()
        self._load_phase_gif(self.timer.phase)
        self._on_tick(self.timer.remaining, self.timer.phase)
        QTimer.singleShot(0, self.snap_to_corner)

    def _flags(self) -> Qt.WindowType:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.store.get("always_on_top"):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        return flags

    def _apply_look(self) -> None:
        self.setWindowFlags(self._flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowOpacity(float(self.store.get("opacity")))
        self.setStyleSheet("background: transparent;")
        self.card.setStyleSheet("background: transparent;")
        self.show()
        family = self.store.get("timer_font_family")
        size = self.store.get("timer_font_size")
        self.time_label.setFont(QFont(family, size, QFont.Weight.Bold))
        self.phase_label.setFont(QFont(family, max(8, size - 10)))
        self.time_label.setStyleSheet(
            f"color: {self.store.get('timer_color')}; background: transparent;"
        )
        self.phase_label.setStyleSheet(
            f"color: {self.store.get('label_color')}; background: transparent;"
        )
        self.gif.setStyleSheet("background: transparent;")
        self.gif.set_gif_size(self.store.get("gif_size"))
        self.adjustSize()

    def _resolve_gif(self, raw: str) -> str:
        if not raw:
            return ""
        path = Path(raw)
        if not path.is_absolute():
            path = GIF_DIR / raw
        return str(path)

    def _load_phase_gif(self, phase: Phase) -> None:
        raw = self.store.get("gifs", {}).get(phase.value, "")
        self.gif.load(self._resolve_gif(raw))

    def _corner_positions(self) -> dict[str, tuple[int, int]]:
        screen = self.screen() or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        margin = int(self.store.get("margin"))
        w, h = self.width(), self.height()
        return {
            "top-left": (geo.left() + margin, geo.top() + margin),
            "top-right": (geo.right() - w - margin, geo.top() + margin),
            "bottom-left": (geo.left() + margin, geo.bottom() - h - margin),
            "bottom-right": (geo.right() - w - margin, geo.bottom() - h - margin),
        }

    def _nearest_corner(self) -> str:
        cx = self.x() + self.width() / 2
        cy = self.y() + self.height() / 2
        nearest = "bottom-right"
        best = float("inf")
        for name, (x, y) in self._corner_positions().items():
            dx = cx - (x + self.width() / 2)
            dy = cy - (y + self.height() / 2)
            dist = dx * dx + dy * dy
            if dist < best:
                best = dist
                nearest = name
        return nearest

    def snap_to_corner(self, corner: str | None = None) -> None:
        name = corner or self.store.get("corner") or self._nearest_corner()
        x, y = self._corner_positions()[name]
        self.move(x, y)
        self.store.update({"corner": name})

    def apply_settings(self) -> None:
        self.timer.apply_settings(
            work_seconds=self.store.get("work_minutes") * 60,
            short_break_seconds=self.store.get("short_break_minutes") * 60,
            long_break_seconds=self.store.get("long_break_minutes") * 60,
            sessions_until_long_break=self.store.get("sessions_until_long_break"),
        )
        self._apply_look()
        self._load_phase_gif(self.timer.phase)
        self.snap_to_corner()

    def open_settings(self) -> None:
        dialog = SettingsWindow(self.store, self)
        if dialog.exec():
            self.store.update(dialog.values())
            self.apply_settings()

    def _on_tick(self, remaining: int, phase: Phase) -> None:
        minutes, seconds = divmod(remaining, 60)
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
        self.phase_label.setText(PHASE_LABELS[phase])

    def _on_phase_change(self, phase: Phase) -> None:
        self._load_phase_gif(phase)
        QApplication.beep()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._dragging:
            self._dragging = False
            self.snap_to_corner(self._nearest_corner())
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.timer.toggle()
        super().mouseDoubleClickEvent(event)

    def _show_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.addAction("Start / Pause", self.timer.toggle)
        menu.addAction("Reset phase", self.timer.reset_phase)
        menu.addAction("Skip phase", self.timer.skip)
        menu.addSeparator()
        menu.addAction("Snap to corner", self.snap_to_corner)
        menu.addAction("Settings", self.open_settings)
        menu.addSeparator()
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        menu.exec(self.mapToGlobal(pos))
