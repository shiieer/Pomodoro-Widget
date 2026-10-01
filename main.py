import sys

from PyQt6.QtWidgets import QApplication

from config import GIF_DIR
from core.settings_store import SettingsStore
from ui.app import PomodoroApp


def main() -> None:
    GIF_DIR.mkdir(parents=True, exist_ok=True)
    app = QApplication(sys.argv)
    # Set to False so hiding the main window while showing the mini widget does not exit the app
    app.setQuitOnLastWindowClosed(False)

    store = SettingsStore()
    app_window = PomodoroApp(store)
    app_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
