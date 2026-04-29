import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from stepanalyzer.gui.widgets.Open_Field_Widget import Open_Field_Widget
from stepanalyzer.gui.widgets.Treadmill_Widget import Treadmill_Widget


class Menu_Widget(QWidget):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        self.res_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "resources/images",
        )

        self.main_layout = QVBoxLayout()
        self.header_layout = QVBoxLayout()
        self.card_layout = QGridLayout()

        self.title = QLabel("Step Analyzer")
        self.subtitle = QLabel(
            "Рабочая среда для траекторий походки, шаговых циклов и многокомпонентного анализа движения."
        )

        self.treadmill_button = self._create_mode_button(
            "Treadmill",
            "Углы, длины сегментов и параметры шагового цикла.",
            "image_kinematics.png",
        )
        self.open_field_button = self._create_mode_button(
            "Open Field",
            "Траектории лап и суставов по синхронным точкам тела.",
            "image_ladder_rung.png",
        )

        self.setup_UI()

    def setup_UI(self):
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(56, 48, 56, 48)
        self.main_layout.setSpacing(28)

        self.title.setObjectName("titleLabel")
        self.subtitle.setObjectName("subtitleLabel")
        self.subtitle.setWordWrap(True)

        self.header_layout.setSpacing(8)
        self.header_layout.addWidget(self.title)
        self.header_layout.addWidget(self.subtitle)
        self.main_layout.addLayout(self.header_layout)

        self.card_layout.setSpacing(18)
        self.card_layout.addWidget(self.treadmill_button, 0, 0)
        self.card_layout.addWidget(self.open_field_button, 0, 1)
        self.main_layout.addLayout(self.card_layout)

        self.main_layout.addWidget(self._create_research_panel())
        self.main_layout.addStretch(1)

        self.treadmill_button.clicked.connect(self.open_treadmill_widget)
        self.open_field_button.clicked.connect(self.open_open_field_widget)

    def _create_mode_button(self, title, description, icon_name):
        button = QPushButton(f"{title}\n{description}")
        button.setObjectName("modeCard")
        button.setMinimumSize(360, 180)
        button.setIcon(QIcon(os.path.join(self.res_path, icon_name)))
        button.setIconSize(QSize(96, 96))
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _create_research_panel(self):
        panel = QFrame()
        panel.setFrameShape(QFrame.StyledPanel)
        panel.setStyleSheet(
            "QFrame { background: #ffffff; border: 1px solid #d8dee6; border-radius: 8px; }"
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(8)
        panel.setLayout(layout)

        section = QLabel("Следующий исследовательский слой")
        section.setObjectName("sectionLabel")
        text = QLabel(
            "Направление развития: исходные траектории -> фильтрованные многокомпонентные сигналы -> "
            "признаки координации -> эксперименты с Калманом и нейросетями."
        )
        text.setObjectName("hintLabel")
        text.setWordWrap(True)

        chips = QHBoxLayout()
        for label in ("Raw vs filtered", "Координация лап", "Динамика восстановления", "Метрики модели"):
            chip = QLabel(label)
            chip.setStyleSheet(
                "QLabel { background: #eef4ff; color: #1f4f88; border-radius: 5px; padding: 5px 8px; }"
            )
            chips.addWidget(chip)
        chips.addStretch(1)

        layout.addWidget(section)
        layout.addWidget(text)
        layout.addLayout(chips)
        return panel

    def open_treadmill_widget(self):
        self.deleteLater()
        self.frame.setCentralWidget(Treadmill_Widget(self.frame))

    def open_open_field_widget(self):
        self.deleteLater()
        self.frame.setCentralWidget(Open_Field_Widget(self.frame))
