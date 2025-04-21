import os
import sys

import cv2
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, pyqtSlot, QCoreApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, \
    QMessageBox, QMainWindow, QComboBox, QListWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class Main_Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.video_cap = None
        self._list_widget = QListWidget()

        self._list_widget.addItem("Item 1")
        self._list_widget.addItem("Item 2")
        self._list_widget.addItem("Item 3")


        # Label for slider
        self.label_count_frame = QLabel('Number Frame')
        self.label_step_distance = QLabel('Step Distance')
        self.label_angle_distance = QLabel('Angle Distance')

        # Widget for video
        self.image_label = QLabel()

        # Widget for plot
        self.figure = Figure(figsize=(4, 3), dpi=80)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Slider for frame navigation
        self._change_frame_slider = QSlider(Qt.Horizontal)
        self._change_step_slider = QSlider(Qt.Horizontal)
        self._change_angle_slider = QSlider(Qt.Horizontal)

        self.next_button = QPushButton("Next")
        self.back_button = QPushButton("Back")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setup_UI_widget()

    def setup_UI_widget(self):
        self.image_label.setFixedSize(900, 900)

        self._change_step_slider.setEnabled(False)
        self._change_angle_slider.setEnabled(False)
        self._change_frame_slider.setEnabled(False)
        # self._change_frame_slider.sliderMoved.connect(self.slider_changed)
        self._change_frame_slider.setMinimum(0)
        self._change_frame_slider.setMinimum(1)
        self._change_frame_slider.setValue(0)
        self._change_frame_slider.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure the slider can take keyboard focus

        figure_layout = QHBoxLayout()
        figure_layout.addWidget(self._list_widget)
        figure_layout.addWidget(self.image_label)
        figure_layout.addWidget(self.canvas)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.next_button)

        slider_layout = QVBoxLayout()
        slider_layout.addLayout(figure_layout)
        slider_layout.addLayout(buttons_layout)
        slider_layout.addWidget(self._change_frame_slider)
        slider_layout.addWidget(self.label_count_frame)
        slider_layout.addWidget(self._change_step_slider)
        slider_layout.addWidget(self.label_step_distance)
        slider_layout.addWidget(self._change_angle_slider)
        slider_layout.addWidget(self.label_angle_distance)

        self.main_layout.addLayout(slider_layout)

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()
