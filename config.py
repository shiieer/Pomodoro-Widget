from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = APP_DIR / "settings.json"
GIF_DIR = APP_DIR / "assets" / "gifs"

TASKS_PATH = APP_DIR / "tasks.json"

DEFAULT_SETTINGS = {
    "work_minutes": 25,
    "short_break_minutes": 5,
    "long_break_minutes": 15,
    "sessions_until_long_break": 4,
    "corner": "bottom-right",
    "margin": 16,
    "always_on_top": True,
    "opacity": 0.97,
    "gif_size": 0,
    "timer_font_family": "Segoe UI",
    "timer_font_size": 42,
    "timer_color": "#F7FAFF",
    "label_color": "#AEB8C9",
    "bg_color": "#151B27",
    "accent_color": "#9EE7FF",
    "gifs": {
        "work": "",
        "short_break": "",
        "long_break": "",
    },
}
