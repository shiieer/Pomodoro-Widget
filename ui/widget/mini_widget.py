from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMenu,
    QVBoxLayout,
    QWidget,
)

from core.timer import Phase
from ui.common import DraggableMixin, snap_widget_to_corner
from ui.icons import get_icon
from ui.widget.constants import widget_font
from ui.widget.mini_button import MiniButton
from ui.widget.painter import paint_mini_widget
from ui.widget.peek_tab import PeekTab

if TYPE_CHECKING:
    from ui.app.app_window import PomodoroApp


class MiniWidget(DraggableMixin, QWidget):
    WIDTH = 210
    HEIGHT = 70
    RADIUS = 18

    _HIDE_DELAY = 3000  # ms idle before hiding
    _FADE_MS = 280  # fade-out duration
    _REVEAL_MS = 260  # fade-in duration

    def __init__(self, app: PomodoroApp):
        super().__init__()
        self.app = app
        self.store = app.store

        self._remaining = 0
        self._total_seconds = 1
        self._phase = Phase.WORK
        self._has_moved_manually = False

        # ── peek tab (separate window) ────────────────────────────────────────
        self._peek_tab = PeekTab(on_click=self._on_tab_clicked)

        # ── idle timer ────────────────────────────────────────────────────────
        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.setInterval(self._HIDE_DELAY)
        self._idle_timer.timeout.connect(self._do_hide)

        # ── fade-out animation ────────────────────────────────────────────────
        self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_anim.setDuration(self._FADE_MS)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InQuad)
        self._fade_anim.finished.connect(self._on_fade_out_done)

        # ── fade-in animation ─────────────────────────────────────────────────
        self._reveal_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._reveal_anim.setDuration(self._REVEAL_MS)
        self._reveal_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._reveal_anim.finished.connect(self._on_reveal_done)

        self._setup_ui()
        self.apply_settings()

    # ── UI construction ───────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.time_label = QLabel("25:00")
        self.time_label.setFont(widget_font(22, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #F7FAFF; background: transparent;")
        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.phase_label = QLabel("FOCUS")
        self.phase_label.setFont(widget_font(8, QFont.Weight.Bold))
        self.phase_label.setStyleSheet(
            "color: #9EE7FF; background: transparent; letter-spacing: 1px;"
        )

        time_box = QVBoxLayout()
        time_box.setContentsMargins(0, 0, 0, 0)
        time_box.setSpacing(1)
        time_box.addWidget(self.phase_label)
        time_box.addWidget(self.time_label)

        self.play_btn = MiniButton(
            get_icon("pause", color="#9EE7FF", size=13), "Pause / Resume"
        )
        self.play_btn.clicked.connect(self._toggle_timer)

        self.expand_btn = MiniButton(
            get_icon("maximize-2", color="#AEB8C9", size=13, active_color="#F7FAFF"),
            "Restore full app (or double-click)",
        )
        self.expand_btn.clicked.connect(self._restore_app)

        self.close_btn = MiniButton(
            get_icon("x", color="#AEB8C9", size=13, active_color="#FF8080"),
            "Quit FocusTimer",
        )
        self.close_btn.clicked.connect(QApplication.quit)

        controls_box = QHBoxLayout()
        controls_box.setContentsMargins(0, 0, 0, 0)
        controls_box.setSpacing(5)
        controls_box.addWidget(self.play_btn)
        controls_box.addWidget(self.expand_btn)
        controls_box.addWidget(self.close_btn)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 14, 12)
        layout.addLayout(time_box)
        layout.addStretch()
        layout.addLayout(controls_box)

    # ── flags / settings ──────────────────────────────────────────────────────

    def _flags(self) -> Qt.WindowType:
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if self.store.get("always_on_top"):
            flags |= Qt.WindowType.WindowStaysOnTopHint
        return flags

    def apply_settings(self) -> None:
        self.setWindowFlags(self._flags())
        self.setWindowOpacity(float(self.store.get("opacity")))
        if not self._has_moved_manually:
            self.snap_to_corner()

    # ── state sync ────────────────────────────────────────────────────────────

    def sync_state(self) -> None:
        self._remaining = self.app.timer.remaining
        self._phase = self.app.timer.phase
        self._total_seconds = max(1, self.app._total_seconds)
        self._update_display()

    def update_tick(self, remaining: int, phase: Phase, total_seconds: int) -> None:
        self._remaining = remaining
        self._phase = phase
        self._total_seconds = max(1, total_seconds)
        self._update_display()
        # keep the tab time current while peeked
        if self._peek_tab.isVisible():
            mins, secs = divmod(max(0, remaining), 60)
            self._peek_tab.update_time(f"{mins:02d}:{secs:02d}")

    def update_phase(self, phase: Phase, total_seconds: int) -> None:
        self._phase = phase
        self._total_seconds = max(1, total_seconds)
        self._update_display()

    def _update_display(self) -> None:
        mins, secs = divmod(self._remaining, 60)
        self.time_label.setText(f"{mins:02d}:{secs:02d}")

        if self._phase == Phase.WORK:
            self.phase_label.setText("FOCUS")
            self.phase_label.setStyleSheet(
                "color: #9EE7FF; background: transparent; font-weight: bold;"
            )
        elif self._phase == Phase.SHORT_BREAK:
            self.phase_label.setText("SHORT BREAK")
            self.phase_label.setStyleSheet(
                "color: #9BE8B8; background: transparent; font-weight: bold;"
            )
        else:
            self.phase_label.setText("LONG BREAK")
            self.phase_label.setStyleSheet(
                "color: #C69EFF; background: transparent; font-weight: bold;"
            )

        if self.app.timer.running:
            self.play_btn.setIcon(get_icon("pause", color="#9EE7FF", size=13))
            self.play_btn.setToolTip("Pause timer")
        else:
            self.play_btn.setIcon(get_icon("play", color="#9EE7FF", size=13))
            self.play_btn.setToolTip("Resume timer")

        self.update()

    # ── nearest screen edge ───────────────────────────────────────────────────

    def _nearest_edge(self) -> str:
        screen = self.screen() or QApplication.primaryScreen()
        geo = screen.availableGeometry()
        pos = self.pos()
        cx = pos.x() + self.WIDTH / 2
        cy = pos.y() + self.HEIGHT / 2
        return min(
            ("top", cy - geo.top()),
            ("bottom", geo.bottom() - cy),
            ("left", cx - geo.left()),
            ("right", geo.right() - cx),
            key=lambda t: t[1],
        )[0]

    # ── hide / peek flow ──────────────────────────────────────────────────────

    def _do_hide(self) -> None:
        """Fade out the MiniWidget, then show the PeekTab."""
        if not self.isVisible():
            return
        # stop any ongoing reveal
        self._reveal_anim.stop()
        # animate opacity to 0
        self._fade_anim.setStartValue(self.windowOpacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.start()

    def _on_fade_out_done(self) -> None:
        """Called when fade-out completes — hide widget, show tab."""
        self.hide()
        # restore opacity so it looks right when shown again
        self.setWindowOpacity(float(self.store.get("opacity", 1.0)))
        # show the tab
        mins, secs = divmod(max(0, self._remaining), 60)
        self._peek_tab.show_at(
            edge=self._nearest_edge(),
            mini_pos=self.pos(),
            mini_w=self.WIDTH,
            mini_h=self.HEIGHT,
            time_text=f"{mins:02d}:{secs:02d}",
        )

    def _on_tab_clicked(self) -> None:
        """PeekTab was clicked — hide tab, reveal MiniWidget."""
        self._peek_tab.hide_tab()
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        # fade in
        target_opa = float(self.store.get("opacity", 1.0))
        self._reveal_anim.setStartValue(0.0)
        self._reveal_anim.setEndValue(target_opa)
        self._reveal_anim.start()

    def _on_reveal_done(self) -> None:
        """Fade-in complete — restart the idle countdown."""
        self._idle_timer.start()

    def _reset_idle_timer(self) -> None:
        self._idle_timer.start()

    # ── show / hide events ────────────────────────────────────────────────────

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._idle_timer.start()

    def hideEvent(self, event) -> None:
        super().hideEvent(event)
        self._idle_timer.stop()

    # ── mouse — any interaction resets idle timer ─────────────────────────────

    def enterEvent(self, event) -> None:
        self._idle_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._idle_timer.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        self._reset_idle_timer()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._reset_idle_timer()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        self._reset_idle_timer()
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._restore_app()
        super().mouseDoubleClickEvent(event)

    # ── paint ─────────────────────────────────────────────────────────────────

    def paintEvent(self, event) -> None:
        paint_mini_widget(self, self._phase, self._remaining, self._total_seconds)

    # ── corner snapping ───────────────────────────────────────────────────────

    def snap_to_corner(self, corner: str | None = None) -> None:
        margin = int(self.store.get("margin"))
        target_corner = corner or self.store.get("corner")
        snap_widget_to_corner(self, margin, target_corner)

    # ── timer actions ─────────────────────────────────────────────────────────

    def _toggle_timer(self) -> None:
        self._reset_idle_timer()
        self.app.timer.toggle()
        self.app.start_btn.setRunning(self.app.timer.running)
        self._update_display()

    def _restore_app(self) -> None:
        self._idle_timer.stop()
        self._peek_tab.hide_tab()
        self.app.restore_from_mini_widget()

    # ── context menu ──────────────────────────────────────────────────────────

    def _show_context_menu(self, pos) -> None:
        self._reset_idle_timer()
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background: #1E2535; color: #F7FAFF; border: 1px solid #2E3A4E;"
            " border-radius: 8px; padding: 4px; font-size: 12px; }"
            "QMenu::item { padding: 6px 20px; border-radius: 4px; }"
            "QMenu::item:selected { background: #2E3A4E; }"
        )
        menu.addAction(
            get_icon("maximize-2", color="#AEB8C9", size=14),
            "Open FocusTimer (App)",
            self._restore_app,
        )
        menu.addSeparator()
        play_icon = get_icon(
            "pause" if self.app.timer.running else "play", color="#9EE7FF", size=14
        )
        play_label = "Pause" if self.app.timer.running else "Resume"
        menu.addAction(play_icon, play_label, self._toggle_timer)
        menu.addAction(
            get_icon("rotate-ccw", color="#AEB8C9", size=14),
            "Reset phase",
            self.app._reset,
        )
        menu.addAction(
            get_icon("skip-forward", color="#AEB8C9", size=14),
            "Skip phase",
            self.app.timer.skip,
        )
        menu.addSeparator()
        menu.addAction(
            get_icon("pin", color="#AEB8C9", size=14),
            "Snap to corner",
            lambda: self.snap_to_corner(),
        )
        menu.addSeparator()
        quit_act = menu.addAction(get_icon("x", color="#FF8080", size=14), "Quit")
        quit_act.triggered.connect(QApplication.quit)
        menu.exec(self.mapToGlobal(pos))
