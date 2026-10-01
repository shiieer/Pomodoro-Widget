from __future__ import annotations

from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QLinearGradient,
    QPainter,
    QPen,
)
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.common import (
    C_ACCENT as _C_ACCENT,
)
from ui.common import (
    C_ACCENT2 as _C_ACCENT2,
)
from ui.common import (
    C_BORDER as _C_BORDER,
)
from ui.common import (
    C_MUTED as _C_MUTED,
)
from ui.common import (
    HDivider,
)

# ── Settings-specific palette constants ───────────────────────────────────────
_C_CARD = QColor(0x0D, 0x14, 0x20, 232)
_C_OFF = QColor(0x1E, 0x29, 0x40)
_C_ICON_BG = QColor(0x8C, 0xDE, 0xFF, 32)


# ── ToggleSwitch ──────────────────────────────────────────────────────────────


class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    W, H = 44, 24

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setFixedSize(self.W, self.H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, value: bool) -> None:
        self._checked = value
        self.update()

    def mousePressEvent(self, _event) -> None:
        self._checked = not self._checked
        self.update()
        self.toggled.emit(self._checked)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(0, 0, self.W, self.H)
        radius = self.H / 2

        if self._checked:
            # Cyan gradient track
            grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
            grad.setColorAt(0.0, _C_ACCENT)
            grad.setColorAt(1.0, _C_ACCENT2)
            p.setPen(QPen(_C_ACCENT, 1.0))
            p.setBrush(QBrush(grad))
        else:
            p.setPen(QPen(_C_BORDER, 1.0))
            p.setBrush(QBrush(_C_OFF))

        p.drawRoundedRect(rect.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

        # Knob
        knob_r = (self.H - 8) / 2
        if self._checked:
            knob_cx = self.W - knob_r - 5
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0x09, 0x21, 0x2D)))
        else:
            knob_cx = knob_r + 5
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(_C_MUTED))

        knob_cy = self.H / 2
        p.drawEllipse(
            QRectF(knob_cx - knob_r, knob_cy - knob_r, knob_r * 2, knob_r * 2)
        )
        p.end()


# ── IconCircle ────────────────────────────────────────────────────────────────

# Map from legacy emoji glyphs to icon names for backward compatibility
_GLYPH_TO_ICON: dict[str, str] = {
    "⏱": "clock",
    "☕": "coffee",
    "🌙": "moon",
    "🔁": "repeat",
    "⏭": "skip-forward",
    "📌": "pin",
    "↔": "grid",
    "🔆": "maximize-2",
    "🖼": "image",
    "🔤": "grid",
    "🔡": "grid",
    "🎨": "palette",
    "🏷": "check",
    "🌑": "moon",
}


class IconCircle(QWidget):
    SIZE = 26

    def __init__(self, glyph: str, parent=None):
        super().__init__(parent)
        # Resolve to an icon name; fall back to text if no mapping
        self._icon_name = _GLYPH_TO_ICON.get(glyph)
        self._fallback_glyph = glyph if not self._icon_name else None
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        rect = QRectF(0, 0, self.SIZE, self.SIZE)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(_C_ICON_BG))
        p.drawRoundedRect(rect, 8, 8)

        if self._icon_name:
            from ui.icons import get_pixmap

            pix = get_pixmap(
                self._icon_name, color="#9EE7FF", size=14, stroke_width=2.0
            )
            offset = (self.SIZE - 14) // 2
            p.drawPixmap(offset, offset, pix)
        else:
            p.setPen(_C_ACCENT)
            p.setFont(QFont("Segoe UI", 11))
            p.drawText(rect, Qt.AlignmentFlag.AlignCenter, self._fallback_glyph)
        p.end()


# ── RowItem ───────────────────────────────────────────────────────────────────


class RowItem(QWidget):
    def __init__(
        self,
        glyph: str,
        title: str,
        sub: str = "",
        control: QWidget | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        icon = IconCircle(glyph)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "color: #F7FAFF; font-size: 13px; background: transparent;"
        )

        text_col = QVBoxLayout()
        text_col.setContentsMargins(0, 0, 0, 0)
        text_col.setSpacing(1)
        text_col.addWidget(title_lbl)

        if sub:
            sub_lbl = QLabel(sub)
            sub_lbl.setStyleSheet(
                "color: #7B879A; font-size: 11px; background: transparent;"
            )
            text_col.addWidget(sub_lbl)

        row = QHBoxLayout(self)
        row.setContentsMargins(16, 10, 16, 10)
        row.setSpacing(10)
        row.addWidget(icon)
        row.addLayout(text_col)
        row.addStretch()

        if control is not None:
            row.addWidget(control)


# ── SectionCard ───────────────────────────────────────────────────────────────


class SectionCard(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SectionCard")

        self._body = QVBoxLayout(self)
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(0)
        self._first = True

        if title:
            title_lbl = QLabel(title)
            title_lbl.setObjectName("SectionTitle")
            title_lbl.setContentsMargins(16, 12, 16, 12)
            self._body.addWidget(title_lbl)
            self._first = False

    def add_row(self, row: QWidget) -> None:
        if not self._first:
            self._body.addWidget(HDivider())
        self._first = False
        self._body.addWidget(row)

    # Convenience: add raw widget without divider
    def add(self, widget: QWidget) -> None:
        self._body.addWidget(widget)


# ── ScrollPage ────────────────────────────────────────────────────────────────


class ScrollPage(QScrollArea):
    def __init__(self, content: QWidget, parent=None):
        super().__init__(parent)
        self.setWidget(content)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setStyleSheet("background: transparent; border: none;")
        content.setStyleSheet("background: transparent;")
