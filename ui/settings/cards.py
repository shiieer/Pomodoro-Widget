from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("Card")

        self.body = QVBoxLayout(self)
        self.body.setContentsMargins(20, 18, 20, 18)
        self.body.setSpacing(12)

        if title:
            heading = QLabel(title)
            heading.setObjectName("CardTitle")
            self.body.addWidget(heading)

    def add(self, widget: QWidget) -> None:
        self.body.addWidget(widget)
