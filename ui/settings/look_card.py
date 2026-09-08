from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDoubleSpinBox,
    QFontComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import DEFAULT_SETTINGS
from ui.settings.cards import Card


class LookCard(QWidget):
    def __init__(self, store, parent=None):
        super().__init__(parent)
        card = Card("Look")

        self.corner = QComboBox()
        self.corner.addItems(["top-left", "top-right", "bottom-left", "bottom-right"])
        self.corner.setCurrentText(store.get("corner"))

        self.margin = QSpinBox()
        self.margin.setRange(0, 200)
        self.margin.setValue(store.get("margin"))

        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.3, 1.0)
        self.opacity.setSingleStep(0.05)
        self.opacity.setValue(store.get("opacity"))

        self.gif_size = QSpinBox()
        self.gif_size.setRange(40, 400)
        self.gif_size.setValue(store.get("gif_size"))

        self.font_family = QFontComboBox()
        self.font_family.setCurrentFont(QFont(store.get("timer_font_family")))

        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(store.get("timer_font_size"))

        self.timer_color = self._color_row(store.get("timer_color"))
        self.label_color = self._color_row(store.get("label_color"))
        self.bg_color = self._color_row(store.get("bg_color"))

        self.always_on_top = QCheckBox("Always on top")
        self.always_on_top.setChecked(bool(store.get("always_on_top")))

        for label, widget in (
            ("Corner", self.corner),
            ("Margin (px)", self.margin),
            ("Opacity", self.opacity),
            ("Image size", self.gif_size),
            ("Font", self.font_family),
            ("Font size", self.font_size),
            ("Timer color", self.timer_color),
            ("Label color", self.label_color),
            ("Background", self.bg_color),
        ):
            card.add(self._row(label, widget))

        card.add(self.always_on_top)

        reset = QPushButton("Reset look")
        reset.clicked.connect(self.reset)
        card.add(reset)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        layout.addStretch()

    def _row(self, label: str, widget: QWidget) -> QWidget:
        wrap = QWidget()
        row = QHBoxLayout(wrap)
        row.setContentsMargins(0, 0, 0, 0)
        text = QLabel(label)
        text.setObjectName("Muted")
        row.addWidget(text)
        row.addStretch()
        row.addWidget(widget)
        return wrap

    def _color_row(self, value: str) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        edit = QLineEdit(value)
        edit.setFixedWidth(110)
        button = QPushButton("Pick")
        button.clicked.connect(lambda: self._pick_color(edit))
        layout.addWidget(edit)
        layout.addWidget(button)
        row.edit = edit
        return row

    def _pick_color(self, edit: QLineEdit) -> None:
        color = QColorDialog.getColor(QColor(edit.text()), self)
        if color.isValid():
            edit.setText(color.name())

    def reset(self) -> None:
        d = DEFAULT_SETTINGS
        self.corner.setCurrentText(d["corner"])
        self.margin.setValue(d["margin"])
        self.opacity.setValue(d["opacity"])
        self.gif_size.setValue(d["gif_size"])
        self.font_family.setCurrentFont(QFont(d["timer_font_family"]))
        self.font_size.setValue(d["timer_font_size"])
        self.timer_color.edit.setText(d["timer_color"])
        self.label_color.edit.setText(d["label_color"])
        self.bg_color.edit.setText(d["bg_color"])
        self.always_on_top.setChecked(bool(d["always_on_top"]))

    def values(self) -> dict:
        return {
            "corner": self.corner.currentText(),
            "margin": self.margin.value(),
            "opacity": self.opacity.value(),
            "gif_size": self.gif_size.value(),
            "timer_font_family": self.font_family.currentFont().family(),
            "timer_font_size": self.font_size.value(),
            "timer_color": self.timer_color.edit.text(),
            "label_color": self.label_color.edit.text(),
            "bg_color": self.bg_color.edit.text(),
            "always_on_top": self.always_on_top.isChecked(),
        }
