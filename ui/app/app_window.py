from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from core.settings_store import SettingsStore
from core.task_store import TaskStore
from core.timer import Phase, PomodoroTimer
from ui.app.buttons import GhostButton, PauseButton
from ui.app.card import DarkCard
from ui.app.constants import PHASE_SUB, HDivider
from ui.app.footer import FooterStrip
from ui.app.header import HeaderBar
from ui.app.progress_ring import ArcProgressRing
from ui.app.session_dots import SessionDots
from ui.app.tabs import PhaseTabBar
from ui.app.task_card import TaskCard
from ui.common import (
    DraggableMixin,
    get_nearest_corner,
    snap_widget_to_corner,
)
from ui.icons import get_icon
from ui.settings import SettingsWindow
from ui.task import TaskPanel
from ui.widget import MiniWidget


class PomodoroApp(DraggableMixin, QWidget):
    def __init__(self, store: SettingsStore):
        super().__init__()
        self.store = store
        self._total_seconds = 1

        # Task store & panel (panel is created lazily on first open)
        self._task_store = TaskStore()
        self._task_panel: TaskPanel | None = None

        self.setWindowTitle("FocusTimer")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")

        # ── Main Dark Card ────────────────────────────────────────────────────
        self.card = DarkCard(self)

        # ── Header ────────────────────────────────────────────────────────────
        self.header = HeaderBar(
            on_settings_clicked=self.open_settings,
            on_close_clicked=self.close_app,
            on_minimize_clicked=self.switch_to_mini_widget,
        )

        # ── Tabs ──────────────────────────────────────────────────────────────
        self.tab_bar = PhaseTabBar(on_switch_phase=self._switch_phase)

        # ── Arc Progress Ring ─────────────────────────────────────────────────
        self.arc = ArcProgressRing()
        arc_row = QHBoxLayout()
        arc_row.setContentsMargins(0, 0, 0, 0)
        arc_row.addStretch()
        arc_row.addWidget(self.arc)
        arc_row.addStretch()

        # ── Session Dots ──────────────────────────────────────────────────────
        sessions_total = int(store.get("sessions_until_long_break"))
        self.session_dots = SessionDots(total=sessions_total)
        dots_row = QHBoxLayout()
        dots_row.setContentsMargins(0, 0, 0, 0)
        dots_row.addStretch()
        dots_row.addWidget(self.session_dots)
        dots_row.addStretch()

        # ── Stats Row ─────────────────────────────────────────────────────────
        self._stats_label = QLabel("Stay with it...")
        self._stats_label.setStyleSheet(
            "color: #AEB8C9; background: transparent; font-size: 9px;"
        )
        self._sessions_count_label = QLabel("0")
        self._sessions_count_label.setStyleSheet(
            "color: #F7FAFF; background: transparent; font-size: 13px; font-weight: 600;"
        )
        stats_row = QHBoxLayout()
        stats_row.setContentsMargins(0, 0, 0, 0)
        stats_row.addWidget(self._stats_label)
        stats_row.addStretch()
        stats_row.addWidget(self._sessions_count_label)

        # ── Action Buttons ────────────────────────────────────────────────────
        self.reset_btn = GhostButton("rotate-ccw", "Reset")
        self.start_btn = PauseButton()
        self.more_btn = GhostButton("more-horizontal")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.more_btn)

        # ── Task Card & Footer ────────────────────────────────────────────────
        self.task_card = TaskCard()
        self.footer = FooterStrip()

        # ── Assemble Card Layout ──────────────────────────────────────────────
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 14, 16, 16)
        card_layout.setSpacing(0)

        card_layout.addWidget(self.header)
        card_layout.addWidget(HDivider())
        card_layout.addSpacing(12)
        card_layout.addWidget(self.tab_bar)
        card_layout.addSpacing(8)
        card_layout.addLayout(arc_row)
        card_layout.addSpacing(8)
        card_layout.addLayout(dots_row)
        card_layout.addSpacing(14)
        card_layout.addLayout(stats_row)
        card_layout.addSpacing(8)
        card_layout.addWidget(HDivider())
        card_layout.addSpacing(10)
        card_layout.addLayout(btn_row)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.task_card)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.footer)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

        # ── Timer Backend ─────────────────────────────────────────────────────
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

        # ── Mini Widget ───────────────────────────────────────────────────────
        self.mini_widget = MiniWidget(self)

        # ── Event Wiring ──────────────────────────────────────────────────────
        self.start_btn.clicked.connect(self._on_start_btn_clicked)
        self.reset_btn.clicked.connect(self._reset)
        # ··· button opens the task panel
        self.more_btn.clicked.connect(self.open_tasks)
        # clicking the task card also opens the task panel
        self.task_card.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_card.mousePressEvent = lambda e: self.open_tasks()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        # ── Initialize State ──────────────────────────────────────────────────
        self._apply_look()
        self.tab_bar.sync_phase(self.timer.phase)
        self._total_seconds = self.timer.remaining
        self._on_tick(self.timer.remaining, self.timer.phase)
        self._refresh_task_card()
        QTimer.singleShot(0, self.snap_to_corner)

    # ── Appearance & Configuration ────────────────────────────────────────────

    def _flags(self) -> Qt.WindowType:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window
        if self.store.get("always_on_top"):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        return flags

    def _apply_look(self) -> None:
        self.setWindowFlags(self._flags())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        opacity = float(self.store.get("opacity", 1.0))
        self.setWindowOpacity(opacity)
        self.show()
        self.adjustSize()

    def close_app(self) -> None:
        """Explicitly quit the entire application."""
        QApplication.quit()

    # ── Timer & Mode Switching ────────────────────────────────────────────────

    def _switch_phase(self, phase: Phase) -> None:
        self.timer.pause()
        self.start_btn.setRunning(False)
        self.timer.phase = phase
        self.timer.remaining = self.timer.durations()[phase]
        self._total_seconds = self.timer.remaining
        self.tab_bar.sync_phase(phase)
        self._on_tick(self.timer.remaining, phase)

    def _on_start_btn_clicked(self) -> None:
        """
        When Start is clicked in the main app:
        - Starts timer
        - Hides main app window
        - Shows compact floating widget
        """
        if not self.timer.running:
            self.timer.running = True
            self.start_btn.setRunning(True)
            self.switch_to_mini_widget()
        else:
            self.timer.pause()
            self.start_btn.setRunning(False)

    def _toggle(self) -> None:
        self.timer.toggle()
        self.start_btn.setRunning(self.timer.running)
        if self.timer.running:
            self.switch_to_mini_widget()

    def switch_to_mini_widget(self) -> None:
        self.hide()
        self.mini_widget.sync_state()
        self.mini_widget.show()
        self.mini_widget.raise_()
        self.mini_widget.activateWindow()

    def restore_from_mini_widget(self) -> None:
        self.mini_widget.hide()
        self.start_btn.setRunning(self.timer.running)
        self.show()
        self.raise_()
        self.activateWindow()

    def _reset(self) -> None:
        self.timer.reset_phase()
        self._total_seconds = self.timer.durations()[self.timer.phase]
        self.start_btn.setRunning(False)
        self.mini_widget.sync_state()

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_tick(self, remaining: int, phase: Phase) -> None:
        minutes, seconds = divmod(remaining, 60)
        time_text = f"{minutes:02d}:{seconds:02d}"

        sub_text = PHASE_SUB[phase]
        completed = self.timer.comleted_work_session
        session_num = str(completed) if completed else ""

        total = max(1, self._total_seconds)
        progress = 1.0 - remaining / total

        self.arc.setState(time_text, sub_text, session_num, progress)

        sessions_per_cycle = int(self.store.get("sessions_until_long_break"))
        self.session_dots.setTotal(sessions_per_cycle)
        self.session_dots.setState(completed % sessions_per_cycle)

        self._sessions_count_label.setText(str(completed))
        if phase == Phase.WORK:
            self._stats_label.setText("Stay with it...")
        elif phase == Phase.SHORT_BREAK:
            self._stats_label.setText("Take a breather")
        else:
            self._stats_label.setText("Long break — rest well")

        self.footer.setState(completed_today=completed, active_page=completed % 5)

        if hasattr(self, "mini_widget") and self.mini_widget:
            self.mini_widget.update_tick(remaining, phase, self._total_seconds)

    def _on_phase_change(self, phase: Phase) -> None:
        self._total_seconds = self.timer.durations()[phase]
        self.tab_bar.sync_phase(phase)
        self.start_btn.setRunning(self.timer.running)
        if hasattr(self, "mini_widget") and self.mini_widget:
            self.mini_widget.update_phase(phase, self._total_seconds)
        QApplication.beep()

    # ── Window Snapping & Dragging ────────────────────────────────────────────

    def _corner_positions(self) -> dict[str, tuple[int, int]]:
        """Return pixel coordinates for each corner. Thin wrapper used by tests."""
        from ui.common.snapper import get_corner_positions

        return get_corner_positions(self, int(self.store.get("margin")))

    def _nearest_corner(self) -> str:
        """Return the corner name closest to the window's current center."""
        return get_nearest_corner(self, int(self.store.get("margin")))

    def snap_to_corner(self, corner: str | None = None) -> None:
        margin = int(self.store.get("margin"))
        target = corner or self.store.get("corner")
        snapped = snap_widget_to_corner(self, margin, target)
        self.store.update({"corner": snapped})

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            margin = int(self.store.get("margin"))
            snapped = snap_widget_to_corner(
                self, margin, get_nearest_corner(self, margin)
            )
            self.store.update({"corner": snapped})

    def closeEvent(self, event) -> None:
        QApplication.quit()

    # ── Settings & Context Menu ───────────────────────────────────────────────

    def apply_settings(self) -> None:
        self.timer.apply_settings(
            work_seconds=self.store.get("work_minutes") * 60,
            short_break_seconds=self.store.get("short_break_minutes") * 60,
            long_break_seconds=self.store.get("long_break_minutes") * 60,
            sessions_until_long_break=self.store.get("sessions_until_long_break"),
        )
        self._total_seconds = self.timer.durations()[self.timer.phase]
        self._apply_look()
        self.snap_to_corner()
        if hasattr(self, "mini_widget") and self.mini_widget:
            self.mini_widget.apply_settings()

    def open_tasks(self) -> None:
        """Open (or raise) the task manager panel."""
        if self._task_panel is None:
            self._task_panel = TaskPanel(self._task_store, self)
            self._task_panel.task_changed.connect(self._refresh_task_card)
        self._task_panel.show()
        self._task_panel.raise_()
        self._task_panel.activateWindow()

    def _refresh_task_card(self) -> None:
        """Sync the main widget's TaskCard with the active task."""
        active = self._task_store.active_task()
        done_count = self._task_store.done_count()
        if active:
            self.task_card.setTask(active["title"], done_count)
        else:
            pending = self._task_store.pending_count()
            if pending:
                self.task_card.setTask(f"{pending} task(s) — tap ··· to manage", 0)
            else:
                self.task_card.setTask("No tasks — tap ··· to add one", 0)

    def open_settings(self) -> None:
        dialog = SettingsWindow(self.store, self)
        if dialog.exec():
            self.store.update(dialog.values())
            self.apply_settings()

    def _show_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: #1E2535; color: #F7FAFF; border: 1px solid #2E3A4E;"
            " border-radius: 8px; padding: 4px; font-size: 12px; }"
            "QMenu::item { padding: 6px 20px; border-radius: 4px; }"
            "QMenu::item:selected { background: #2E3A4E; }"
        )
        play_icon = get_icon(
            "pause" if self.timer.running else "play", color="#9EE7FF", size=14
        )
        play_label = "Pause" if self.timer.running else "Start"
        menu.addAction(play_icon, play_label, self._toggle)
        menu.addAction(
            get_icon("rotate-ccw", color="#AEB8C9", size=14), "Reset phase", self._reset
        )
        menu.addAction(
            get_icon("skip-forward", color="#AEB8C9", size=14),
            "Skip phase",
            self.timer.skip,
        )
        menu.addSeparator()
        menu.addAction(
            get_icon("check-square", color="#9EE7FF", size=14), "Tasks", self.open_tasks
        )
        menu.addSeparator()
        menu.addAction(
            get_icon("minimize-2", color="#AEB8C9", size=14),
            "Switch to Mini Widget",
            self.switch_to_mini_widget,
        )
        menu.addAction(
            get_icon("pin", color="#AEB8C9", size=14),
            "Snap to corner",
            self.snap_to_corner,
        )
        menu.addAction(
            get_icon("settings", color="#AEB8C9", size=14),
            "Settings",
            self.open_settings,
        )
        menu.addSeparator()
        quit_action = menu.addAction(get_icon("x", color="#FF8080", size=14), "Quit")
        quit_action.triggered.connect(QApplication.quit)
        menu.exec(self.mapToGlobal(pos))


# Compatibility alias
PomodoroWidget = PomodoroApp
