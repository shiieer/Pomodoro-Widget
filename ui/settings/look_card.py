from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_SETTINGS
from ui.settings.cards import RowItem, ScrollPage, SectionCard, ToggleSwitch


class LookCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)

        # ── controls ──────────────────────────────────────────────────────────
        self.corner = QComboBox()
        self.corner.addItems(["top-left", "top-right", "bottom-left", "bottom-right"])
        self.corner.setCurrentText(store.get("corner"))
        self.corner.setFixedWidth(130)

        self.margin = QSpinBox()
        self.margin.setRange(0, 200)
        self.margin.setValue(store.get("margin"))
        self.margin.setSuffix(" px")
        self.margin.setFixedWidth(90)

        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.1, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setValue(store.get("opacity"))
        self.opacity.setFixedWidth(90)

        self.gif_size = QSpinBox()
        self.gif_size.setRange(40, 400)
        self.gif_size.setValue(store.get("gif_size"))
        self.gif_size.setSuffix(" px")
        self.gif_size.setFixedWidth(90)

        self.font_family = QFontComboBox()
        self.font_family.setCurrentFont(QFont(store.get("timer_font_family")))
        self.font_family.setFixedWidth(160)

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(store.get("timer_font_size"))
        self.font_size.setSuffix(" pt")
        self.font_size.setFixedWidth(90)

        self._timer_color_edit = self._make_color_edit(store.get("timer_color"))
        self._label_color_edit = self._make_color_edit(store.get("label_color"))
        self._bg_color_edit = self._make_color_edit(store.get("bg_color"))

        timer_color_row = self._color_widget(self._timer_color_edit)
        label_color_row = self._color_widget(self._label_color_edit)
        bg_color_row = self._color_widget(self._bg_color_edit)

        self.always_on_top = ToggleSwitch(bool(store.get("always_on_top")))

        # ── card ──────────────────────────────────────────────────────────────
        card = SectionCard("Appearance")
        card.add_row(RowItem("📌", "Corner", "Widget snap position", self.corner))
        card.add_row(RowItem("↔", "Margin", "Distance from screen edge", self.margin))
        card.add_row(
            RowItem(
                "🔆", "Opacity", "Widget transparency (1 = fully visible)", self.opacity
            )
        )
        card.add_row(
            RowItem("🖼", "Image size", "Pixel size of per-phase images", self.gif_size)
        )
        card.add_row(RowItem("🔤", "Font", "Timer digit font family", self.font_family))
        card.add_row(RowItem("🔡", "Font size", "Timer digit size", self.font_size))
        card.add_row(
            RowItem(
                "🎨", "Timer colour", "Hex colour for the big digits", timer_color_row
            )
        )
        card.add_row(
            RowItem(
                "🏷", "Label colour", "Hex colour for the phase label", label_color_row
            )
        )
        card.add_row(
            RowItem("🌑", "Background", "Widget background colour", bg_color_row)
        )
        card.add_row(
            RowItem(
                "📌",
                "Always on top",
                "Keep widget above other windows",
                self.always_on_top,
            )
        )

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(16)
        lay.addWidget(card)
        lay.addStretch()

        page = ScrollPage(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(page)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _make_color_edit(self, value: str) -> QLineEdit:
        edit = QLineEdit(value)
        edit.setFixedWidth(90)
        return edit

    def _color_widget(self, edit: QLineEdit) -> QWidget:
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        btn = QPushButton("Pick")
        btn.setFixedWidth(46)
        btn.clicked.connect(lambda: self._pick_color(edit))
        lay.addWidget(edit)
        lay.addWidget(btn)
        return wrap

    def _pick_color(self, edit: QLineEdit) -> None:
        color = QColorDialog.getColor(QColor(edit.text()), self)
        if color.isValid():
            edit.setText(color.name())

    # ── public API ────────────────────────────────────────────────────────────

    def reset(self) -> None:
        d = DEFAULT_SETTINGS
        self.corner.setCurrentText(d["corner"])
        self.margin.setValue(d["margin"])
        self.opacity.setValue(d["opacity"])
        self.gif_size.setValue(d["gif_size"])
        self.font_family.setCurrentFont(QFont(d["timer_font_family"]))
        self.font_size.setValue(d["timer_font_size"])
        self._timer_color_edit.setText(d["timer_color"])
        self._label_color_edit.setText(d["label_color"])
        self._bg_color_edit.setText(d["bg_color"])
        self.always_on_top.setChecked(bool(d["always_on_top"]))

    def values(self) -> dict:
        return {
            "corner": self.corner.currentText(),
            "margin": self.margin.value(),
            "opacity": self.opacity.value(),
            "gif_size": self.gif_size.value(),
            "timer_font_family": self.font_family.currentFont().family(),
            "timer_font_size": self.font_size.value(),
            "timer_color": self._timer_color_edit.text(),
            "label_color": self._label_color_edit.text(),
            "bg_color": self._bg_color_edit.text(),
            "always_on_top": self.always_on_top.isChecked(),
        }
