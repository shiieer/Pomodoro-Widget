import sys

from PyQt6.QtWidgets import QApplication

from config import GIF_DIR
from core.settings_store import SettingsStore
from ui.widget import PomodoroWidget


def main() -> None:
    GIF_DIR.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    store = SettingsStore()
    widget = PomodoroWidget(store)
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
