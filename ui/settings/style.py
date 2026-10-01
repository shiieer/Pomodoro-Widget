SETTINGS_QSS = """
/* ── Window / root ──────────────────────────────────────────────── */
QDialog {
    background: #151B27;
    color: #F7FAFF;
    font-family: "Segoe UI";
    font-size: 13px;
}
QWidget#Root {
    background: #151B27;
    color: #F7FAFF;
    font-family: "Segoe UI";
    font-size: 13px;
}

/* ── Generic labels ─────────────────────────────────────────────── */
QLabel {
    color: #F7FAFF;
    background: transparent;
}
QLabel#Muted {
    color: #AEB8C9;
    font-size: 12px;
}
QLabel#Dim {
    color: #7B879A;
    font-size: 11px;
}
QLabel#SectionTitle {
    color: #F7FAFF;
    font-size: 15px;
    font-weight: 600;
}
QLabel#PageTitle {
    color: #F7FAFF;
    font-size: 18px;
    font-weight: 700;
}
QLabel#AppDesc {
    color: #AEB8C9;
    font-size: 11px;
}

/* ── Section cards (#0D1420 dark bg + white border) ─────────────── */
QFrame#SectionCard {
    background: rgba(13,20,32,0.91);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
}

/* ── Nav sidebar ─────────────────────────────────────────────────── */
QListWidget#NavList {
    background: transparent;
    border: none;
    outline: none;
}
QListWidget#NavList::item {
    color: #AEB8C9;
    padding: 9px 14px;
    border-radius: 8px;
    margin: 1px 0;
    font-size: 13px;
}
QListWidget#NavList::item:selected {
    background: rgba(255,255,255,0.08);
    color: #F7FAFF;
    border: 1px solid rgba(255,255,255,0.12);
}
QListWidget#NavList::item:hover:!selected {
    background: rgba(255,255,255,0.05);
}

/* ── Input controls ─────────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QFontComboBox {
    background: #0D1420;
    color: #F7FAFF;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 7px;
    padding: 5px 9px;
    min-height: 28px;
    min-width: 80px;
    font-size: 12px;
}
QSpinBox:focus, QDoubleSpinBox:focus,
QComboBox:focus, QLineEdit:focus {
    border: 1px solid #9EE7FF;
}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}
QComboBox::drop-down {
    border: none;
    background: transparent;
    width: 22px;
}
QComboBox QAbstractItemView {
    background: #0D1420;
    color: #F7FAFF;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 6px;
    selection-background-color: rgba(158,231,255,0.15);
}

/* ── Buttons ─────────────────────────────────────────────────────── */
QPushButton {
    background: rgba(255,255,255,0.07);
    color: #F7FAFF;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 12px;
}
QPushButton:hover {
    background: rgba(255,255,255,0.11);
}
QPushButton:pressed {
    background: rgba(255,255,255,0.05);
}
QPushButton#Accent {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #9EE7FF, stop:1 #50C8F3);
    color: #09212D;
    font-weight: 700;
    font-size: 13px;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
}
QPushButton#Accent:hover {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #b8f0ff, stop:1 #7adeff);
}
QPushButton#Ghost {
    background: transparent;
    color: #AEB8C9;
    border: none;
    padding: 6px 12px;
    font-size: 12px;
}
QPushButton#Ghost:hover {
    color: #F7FAFF;
}

/* ── Checkbox ─────────────────────────────────────────────────────── */
QCheckBox {
    color: #F7FAFF;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,0.25);
    background: #0D1420;
}
QCheckBox::indicator:checked {
    background: #9EE7FF;
    border: 1px solid #9EE7FF;
    image: none;
}

/* ── Scrollbar ────────────────────────────────────────────────────── */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(255,255,255,0.15);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ── Drop slot (media preview) ───────────────────────────────────── */
QFrame#DropSlot {
    background: rgba(13,20,32,0.91);
    border: 1px dashed rgba(255,255,255,0.2);
    border-radius: 10px;
}
QFrame#DropSlot[hover="true"] {
    border: 1px dashed #9EE7FF;
    background: rgba(158,231,255,0.06);
}
"""
