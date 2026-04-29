APP_STYLE = """
QMainWindow {
    background: #f4f6f8;
}

QMenuBar {
    background: #ffffff;
    border-bottom: 1px solid #d8dee6;
    color: #1f2937;
    padding: 4px 8px;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}

QMenuBar::item:selected {
    background: #e9eef5;
    border-radius: 4px;
}

QMenu {
    background: #ffffff;
    border: 1px solid #d8dee6;
    padding: 6px;
}

QMenu::item {
    padding: 7px 24px;
}

QMenu::item:selected {
    background: #e7f0ff;
    color: #0f4c81;
}

QWidget {
    font-family: "Segoe UI", "Arial";
    font-size: 13px;
    color: #1f2937;
}

QLabel#titleLabel {
    color: #111827;
    font-size: 28px;
    font-weight: 700;
}

QLabel#subtitleLabel {
    color: #526173;
    font-size: 14px;
}

QLabel#sectionLabel {
    color: #111827;
    font-size: 15px;
    font-weight: 600;
}

QLabel#hintLabel {
    color: #687386;
    font-size: 12px;
}

QPushButton {
    background: #ffffff;
    border: 1px solid #cfd8e3;
    border-radius: 6px;
    color: #1f2937;
    padding: 8px 12px;
}

QPushButton:hover {
    background: #f6f9fc;
    border-color: #91a4ba;
}

QPushButton:pressed {
    background: #e8eef6;
}

QPushButton:disabled {
    background: #eef1f5;
    border-color: #d8dee6;
    color: #99a3af;
}

QPushButton#primaryButton {
    background: #1f6feb;
    border-color: #1f6feb;
    color: #ffffff;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background: #1a60c8;
}

QPushButton#modeCard {
    background: #ffffff;
    border: 1px solid #d8dee6;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    padding: 16px;
    text-align: left;
}

QPushButton#modeCard:hover {
    background: #f8fbff;
    border-color: #6ca3f7;
}

QSlider::groove:horizontal {
    background: #d8dee6;
    border-radius: 3px;
    height: 6px;
}

QSlider::handle:horizontal {
    background: #1f6feb;
    border: 2px solid #ffffff;
    border-radius: 8px;
    margin: -5px 0;
    width: 16px;
}

QSpinBox {
    background: #ffffff;
    border: 1px solid #cfd8e3;
    border-radius: 5px;
    padding: 4px 8px;
}
"""


def apply_app_style(app):
    app.setStyleSheet(APP_STYLE)
