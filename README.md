# Pomodoro Widget

A minimal, always-on-top Pomodoro timer widget for your desktop — built with Python and PyQt6.  
Drop a GIF or image for each phase and keep focused in style.

---

## ✨ Features

- **Always-on-top** frameless widget that lives in any corner of your screen
- **Three phases** — Focus, Short Break, and Long Break — with automatic cycling
- **Custom GIF / image** per phase (drag & drop supported)
- **Right-click context menu** — Start/Pause, Reset, Skip, Settings, Quit
- **Double-click** to toggle Start / Pause
- **Drag to reposition** — snaps back to the nearest corner on release
- **Settings window** with three pages:
  - ⏱ **Timer** — duration per phase, sessions until long break
  - 🎨 **Look** — font, colors, opacity, widget corner & margin
  - 🖼 **Media** — assign images/GIFs per phase via drag & drop

---

## 📋 Requirements

- Python 3.10+
- PyQt6

---

## 🚀 Getting Started

### 1. Clone the repo

`
git clone https://github.com/your-username/pomodoro_widget.git
cd pomodoro_widget
`

### 2. Create & activate a virtual environment

`
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
`

### 3. Install dependencies

`
pip install PyQt6
`

### 4. Run

`
python main.py
`

---

## ⚙️ Configuration

Settings are stored in settings.json (auto-generated on first run).  
Copy the example to get started:


| Key | Default | Description |
|---|---|---|
| work_minutes | 25 | Focus session length |
| short_break_minutes | 5 | Short break length |
| long_break_minutes | 15 | Long break length |
| sessions_until_long_break | 4 | Work sessions before a long break |
| corner | bottom-right | Starting corner (	op-left, 	op-right, bottom-left, bottom-right) |
| margin | 16 | Pixel margin from screen edge |
| always_on_top | 	rue | Keep widget above other windows |
| opacity | 0.95 | Widget opacity (0.0 – 1.0) |
| gif_size | 120 | GIF/image display size in pixels |
| 	imer_font_family | Segoe UI | Font for the timer |
| 	imer_font_size | 22 | Font size for the timer |
| 	imer_color | #FFFFFF | Timer text color |
| label_color | #A8A8A8 | Phase label text color |
| bg_color | #1E1E1E | Background color |
| gifs.work | "" | Path to image/GIF for Focus phase |
| gifs.short_break | "" | Path to image/GIF for Short Break phase |
| gifs.long_break | "" | Path to image/GIF for Long Break phase |

---

## 🖱️ Usage

| Action | Result |
|---|---|
| Double-click | Start / Pause timer |
| Right-click | Open context menu |
| Drag | Move widget; snaps to nearest corner on release |

### Context Menu

| Option | Description |
|---|---|
| Start / Pause | Toggle the timer |
| Reset phase | Restart the current phase |
| Skip phase | Jump to the next phase immediately |
| Snap to corner | Re-snap to the saved corner |
| Settings | Open the settings window |
| Quit | Exit the app |

---

## 📁 Project Structure

`
pomodoro_widget/
├── main.py                  # Entry point
├── config.py                # Paths & default settings
├── settings.example.json    # Example config (copy to settings.json)
├── assets/
│   └── gifs/                # Place your GIF/image assets here
├── core/
│   ├── timer.py             # Pomodoro timer logic & phase management
│   └── settings_store.py    # Persistent settings read/write
└── ui/
    ├── widget.py            # Main desktop widget
    ├── gif_player.py        # Animated GIF / image display
    ├── settings_window.py   # Settings dialog
    └── settings/
        ├── timer_card.py    # Timer settings page
        ├── look_card.py     # Appearance settings page
        ├── media_card.py    # Media assignment page
        ├── media_preview.py # Drag-and-drop image preview
        ├── sidebar.py       # Settings navigation sidebar
        └── style.py         # QSS stylesheet
`

---
