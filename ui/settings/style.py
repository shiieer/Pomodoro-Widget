SETTINGS_QSS = """
QDialog#SettingsWindow {
    background: #1C1C1C;
}
QWidget#Root {
    background: #1C1C1C;
    color: #FFFFFF;
    font-family: "Segoe UI";
    font-size: 13px;
}
QLabel {
    color: #FFFFFF;
    background: transparent;
}
QLabel#Muted {
    color: #B3B3B3;
}
QLabel#CardTitle {
    font-size: 18px;
    font-weight: 600;
}
QLabel#BigTime {
    font-size: 28px;
    font-weight: 600;
}
QFrame#Card {
    background: #2C2C2C;
    border: 1px solid #3A3A3A;
    border-radius: 12px;
}
QListWidget#Sidebar {
    background: #202020;
    border: none;
    border-radius: 8px;
    padding: 8px;
    outline: none;
}
QListWidget#Sidebar::item {
    color: #E6E6E6;
    padding: 10px 14px;
    border-radius: 6px;
    margin: 2px 0;
}
QListWidget#Sidebar::item:selected {
    background: #3A3A3A;
    color: #FFFFFF;
}
QListWidget#Sidebar::item:hover {
    background: #333333;
}
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QFontComboBox {
    background: #1C1C1C;
    color: #FFFFFF;
    border: 1px solid #3F3F3F;
    border-radius: 8px;
    padding: 6px 8px;
    min-height: 28px;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
    border: 1px solid #60CDFF;
}
QPushButton {
    background: #3A3A3A;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
}
QPushButton:hover {
    background: #474747;
}
QPushButton#Accent {
    background: #60CDFF;
    color: #003543;
    font-weight: 600;
    padding: 10px 18px;
    border-radius: 8px;
}
QPushButton#Accent:hover {
    background: #7AD4FF;
}
QCheckBox {
    color: #E6E6E6;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #7A7A7A;
    background: #1C1C1C;
}
QCheckBox::indicator:checked {
    background: #60CDFF;
    border: 1px solid #60CDFF;
}
QFrame#DropSlot {
    background: #1C1C1C;
    border: 1px dashed #5A5A5A;
    border-radius: 10px;
}
QFrame#DropSlot[hover="true"] {
    border: 1px dashed #60CDFF;
    background: #243036;
}
"""
