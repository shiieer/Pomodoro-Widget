from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = APP_DIR / "settings.json"
GIF_DIR = APP_DIR / "assets" / "gifs"

DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_until_long_break": 4,
    "corner": "bottom-right",
    "margin": 16,
    "always_on_top": True,
    "opacity": 0.95,
    "gif_size": 120,
    "timer_font_family": "Segoe UI",
    "timer_font_size": 22,
    "timer_color": "#FFFFFF",
    "label_color": "#A8A8A8",
    "bg_color": "#1E1E1E",
    "gifs": {
        "work": "",
        "short_break": "",
        "long_break": "",
    },
}
