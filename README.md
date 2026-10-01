# FocusTimer

A dark-themed, always-on-top Pomodoro timer for your desktop — built with Python and PyQt6.

Sits in a corner of your screen while you work, shows a circular arc progress ring, tracks your sessions, and lets you manage a personal task list.

---

## ✨ Features

- **Circular arc progress ring** with a glowing cyan tip
- **Three phases** — Focus, Short Break, Long Break — with automatic cycling
- **Session dots** showing progress through the current work cycle
- **Task list** — add, complete, delete, and prioritise tasks; the active task shows on the widget
- **Mini widget mode** — collapses to a compact floating pill when the timer starts
- **Drag to reposition** — snaps to the nearest screen corner on release
- **Right-click context menu** on both the main widget and the mini widget
- **Settings window** with three pages:
  - ⏱ **Timer** — work/break durations, sessions until long break, skip breaks toggle
  - 🎨 **Look** — font, colours, opacity, corner, margin, always-on-top
  - 🖼 **Media** — assign an image or animated GIF per phase

---

## 📋 Requirements

- Python 3.10+
- PyQt6
- PyQt6-Qt6 / PyQt6-sip (installed automatically with PyQt6)

---

## 🚀 Getting Started

### 1. Clone

```bash
git clone https://github.com/your-username/pomodoro_widget.git
cd pomodoro_widget
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install PyQt6
```

### 4. Run

```bash
python main.py
```

---

## 🖱️ Usage

### Main window

| Action | Result |
|---|---|
| Click **▶ Start** | Start the timer and switch to the compact mini widget |
| Click **⏸ Pause** (mini widget) | Pause the timer |
| Click **↺ Reset** | Restart the current phase |
| Click **···** | Open the task panel |
| Click the task card | Open the task panel |
| Drag title bar area | Move the window |
| Right-click | Open context menu |
| Click **⚙** | Open settings |

### Mini widget

| Action | Result |
|---|---|
| **⏸ / ▶** button | Pause / resume |
| **⤢** button | Restore the full app |
| **✕** button | Quit |
| Double-click | Restore the full app |
| Drag | Move widget; snaps to nearest corner on release |
| Right-click | Context menu |

### Task panel

| Action | Result |
|---|---|
| Type + press Enter or **+ Add** | Add a new task |
| **○ / ◉** icon | Mark / unmark as done |
| **▶** icon | Set as the active focus task |
| **✕** icon | Delete task |
| **Clear completed** | Remove all done tasks |

---

## ⚙️ Settings reference

Settings are persisted to `settings.json` (created automatically on first run; not committed to git).

| Key | Default | Description |
|---|---|---|
| `work_minutes` | `25` | Focus session length (minutes) |
| `short_break_minutes` | `5` | Short break length (minutes) |
| `long_break_minutes` | `15` | Long break length (minutes) |
| `sessions_until_long_break` | `4` | Work sessions before a long break |
| `skip_breaks` | `false` | Go straight back to Focus after each session |
| `corner` | `"bottom-right"` | Widget snap position (`top-left`, `top-right`, `bottom-left`, `bottom-right`) |
| `margin` | `16` | Pixel gap from screen edge |
| `always_on_top` | `true` | Keep widget above all other windows |
| `opacity` | `0.97` | Window opacity (0.1 – 1.0) |
| `timer_font_family` | `"Segoe UI"` | Font used for the timer digits |
| `timer_font_size` | `42` | Timer digit size (pt) |
| `timer_color` | `"#F7FAFF"` | Timer text colour |
| `label_color` | `"#AEB8C9"` | Phase label colour |
| `bg_color` | `"#151B27"` | Widget background colour |
| `accent_color` | `"#9EE7FF"` | Accent / highlight colour |
| `gif_size` | `0` | GIF/image display size in pixels (0 = hidden) |
| `gifs.work` | `""` | Path to image/GIF shown during Focus |
| `gifs.short_break` | `""` | Path to image/GIF shown during Short Break |
| `gifs.long_break` | `""` | Path to image/GIF shown during Long Break |

Tasks are persisted to `tasks.json` (also local-only, not committed to git).

---

## 📁 Project structure

```
pomodoro_widget/
├── main.py                     # Entry point
├── config.py                   # Paths & default settings constants
├── pytest.ini                  # Test runner configuration
│
├── assets/
│   └── gifs/                   # Place your GIF/image assets here
│       └── .gitkeep
│
├── core/
│   ├── timer.py                # PomodoroTimer — phase logic, callbacks
│   ├── settings_store.py       # JSON settings read/write with deep-merge
│   └── task_store.py           # JSON task list (add, complete, delete, persist)
│
├── ui/
│   ├── icons.py                # SVG icon system (get_icon, get_pixmap, SvgIconWidget)
│   ├── gif_player.py           # Animated GIF / static image player widget
│   ├── settings_window.py      # Re-export shim → ui/settings/settings_window.py
│   ├── task_panel.py           # Re-export shim → ui/task/panel.py
│   │
│   ├── app/                    # Main application window components
│   │   ├── app_window.py       # PomodoroApp — main window orchestrator
│   │   ├── card.py             # DarkCard — the outer rounded dark container
│   │   ├── header.py           # HeaderBar + HeaderIcon
│   │   ├── tabs.py             # PhaseTabBar — Focus / BReak tabs
│   │   ├── progress_ring.py    # ArcProgressRing — circular timer arc
│   │   ├── session_dots.py     # SessionDots — cycle progress dots
│   │   ├── footer.py           # FooterStrip — page dots + "N completed today"
│   │   ├── task_card.py        # TaskCard — current task display card
│   │   ├── buttons.py          # GhostButton, PauseButton
│   │   └── constants.py        # Shared colours, fonts, HDivider
│   │
│   ├── widget/                 # Compact floating mini widget
│   │   ├── mini_widget.py      # MiniWidget — pill-shaped overlay
│   │   ├── mini_button.py      # MiniButton — small icon button
│   │   ├── painter.py          # paint_mini_widget — custom background painting
│   │   └── constants.py        # Mini widget colour constants
│   │
│   ├── settings/               # Settings window pages
│   │   ├── settings_window.py  # SettingsWindow dialog
│   │   ├── timer_card.py       # Timer settings page
│   │   ├── look_card.py        # Appearance settings page
│   │   ├── media_card.py       # Media assignment page
│   │   ├── media_preview.py    # Drag-and-drop image/GIF preview slot
│   │   ├── sidebar.py          # Left navigation list
│   │   ├── cards.py            # SectionCard, RowItem, ToggleSwitch, ScrollPage
│   │   └── style.py            # QSS stylesheet
│   │
│   └── task/                   # Task panel components
│       ├── panel.py            # TaskPanel dialog
│       ├── task_row.py         # TaskRow — single interactive task row
│       ├── section.py          # TaskSection — grouped card container
│       └── style.py            # Task panel QSS
│
└── tests/
    ├── conftest.py                     # Headless Qt setup, sys.path config
    ├── test_timer.py                   # PomodoroTimer — 30 tests
    ├── test_task_store.py              # TaskStore — 43 tests
    ├── test_settings_store.py          # SettingsStore — 15 tests
    ├── test_ui_smoke.py                # UI instantiation & smoke — 47 tests
    ├── test_app_window_extended.py     # PomodoroApp behaviour — 37 tests
    ├── test_mini_widget_extended.py    # MiniWidget behaviour — 28 tests
    ├── test_task_ui.py                 # TaskRow/Section/Panel/Settings — 54 tests
    └── test_icons.py                   # Icon system — 8 tests
```

---

## 🧪 Running tests

```bash
# Run all 262 tests (headless, no display needed)
python -m pytest

# Run a specific file
python -m pytest tests/test_timer.py

# Verbose output
python -m pytest -v
```

All tests run headless via the Qt `offscreen` platform — no display or screen required.

---
