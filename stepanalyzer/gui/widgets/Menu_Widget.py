import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel, QVBoxLayout

from stepanalyzer.gui.widgets.Main_Widget import Main_Widget


class Menu_Widget(QWidget):
    def __init__(self, frame):
        super().__init__()
        self.open_field_button = QPushButton()
        self.treadmill_button = QPushButton()
        self.title = QLabel()
        self.frame = frame
        self.res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources/images")

        self.main_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()

        self.setup_UI()

    def setup_UI(self):
        super().__init__()

        self.set_icon_on_buttons()

        self.title.setText("Выберите тип теста для анализа")
        self.title.setFont(QFont('Arial', 15))

        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.button_layout)

        self.button_layout.addWidget(self.open_field_button)
        self.button_layout.addWidget(self.treadmill_button)

        self.treadmill_button.clicked.connect(self.open_treadmill_widget)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.main_layout)


    def set_icon_on_buttons(self):
        self.open_field_button.setIcon(QIcon(os.path.join(self.res_path, "image_kinematics.png")))
        self.open_field_button.setIconSize(self.open_field_button.size())

        self.treadmill_button.setIcon(QIcon(os.path.join(self.res_path, "image_ladder_rung.png")))
        self.treadmill_button.setIconSize(self.treadmill_button.size())

    def open_treadmill_widget(self):
        self.deleteLater()
        self.setup_UI()

        self.frame.setCentralWidget(Main_Widget())
