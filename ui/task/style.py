from ui.common import (
    HEX_ACCENT as C_ACCENT,
)
from ui.common import (
    HEX_ACCENT2 as C_ACCENT2,
)
from ui.common import (
    HEX_ACTIVE_BG as C_ACTIVE_BG,
)
from ui.common import (
    HEX_BG as C_BG,
)
from ui.common import (
    HEX_BORDER as C_BORDER,
)
from ui.common import (
    HEX_CARD_BG as C_CARD_BG,
)
from ui.common import (
    HEX_DIM as C_DIM,
)
from ui.common import (
    HEX_DONE_BG as C_DONE_BG,
)
from ui.common import (
    HEX_GREEN as C_GREEN,
)
from ui.common import (
    HEX_MUTED as C_MUTED,
)
from ui.common import (
    HEX_TEXT as C_TEXT,
)

TASK_QSS = f"""
QDialog {{
    background: {C_BG};
    color: {C_TEXT};
    font-family: "Segoe UI";
    font-size: 13px;
}}
QWidget {{
    background: transparent;
    color: {C_TEXT};
    font-family: "Segoe UI";
}}
QLineEdit {{
    background: rgba(13,20,32,0.93);
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 9px;
    padding: 8px 12px;
    font-size: 13px;
    min-height: 32px;
}}
QLineEdit:focus {{
    border: 1px solid {C_ACCENT};
}}
QPushButton {{
    background: rgba(255,255,255,0.07);
    color: {C_TEXT};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
}}
QPushButton:hover {{
    background: rgba(255,255,255,0.12);
}}
QPushButton#AddBtn {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {C_ACCENT}, stop:1 {C_ACCENT2});
    color: #09212D;
    font-weight: 700;
    border: none;
    border-radius: 9px;
    padding: 8px 18px;
    min-height: 34px;
}}
QPushButton#AddBtn:hover {{
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #b8f0ff, stop:1 #7adeff);
}}
QPushButton#DangerBtn {{
    background: transparent;
    color: {C_DIM};
    border: none;
    padding: 4px 8px;
    font-size: 11px;
}}
QPushButton#DangerBtn:hover {{
    color: #ff7b7b;
}}
QPushButton#IconBtn {{
    background: transparent;
    color: {C_DIM};
    border: none;
    padding: 2px 6px;
    font-size: 13px;
    min-width: 26px;
    max-width: 26px;
    min-height: 26px;
    max-height: 26px;
}}
QPushButton#IconBtn:hover {{
    color: {C_TEXT};
    background: #ffffff14;
    border-radius: 6px;
}}
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255,255,255,0.15);
    border-radius: 2px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QFrame#TaskSection {{
    background: rgba(13,20,32,0.93);
    border: 1px solid {C_BORDER};
    border-radius: 12px;
}}
"""

__all__ = [
    "C_ACCENT",
    "C_ACCENT2",
    "C_ACTIVE_BG",
    "C_BG",
    "C_BORDER",
    "C_CARD_BG",
    "C_DIM",
    "C_DONE_BG",
    "C_GREEN",
    "C_MUTED",
    "C_TEXT",
    "TASK_QSS",
]
