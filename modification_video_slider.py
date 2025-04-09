import os
import sys
import random

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, \
    QMainWindow, QSpinBox, QSlider, QFormLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_gui()
        self.video_loaded = False
        self.csv_data = pd.DataFrame()
        self.coordinates = {}
        self.video_cap = None
        self.current_frame = 0
        self.min_frame = 0
        self.max_frame = 0
        self.total_frames = 0

        # Define colors for the dots (RGB format)
        self.colors = [
            (255, 0, 0),  # Red
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (255, 255, 0),  # Yellow
            (255, 165, 0),  # Orange
            (0, 255, 255),  # Cyan
            (255, 0, 255),  # Magenta
            (128, 0, 128),  # Purple
            (0, 128, 128),  # Teal
            (128, 128, 0),  # Olive
        ]

    def _init_gui(self):

        self.setWindowTitle("Image and Trajectory Plot")

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.load_image("your_image.png")

        self.plot_widget = PlotWidget()

        # 3. Layout
        main_layout = QVBoxLayout()

        # Create a horizontal layout to hold the image and plot side-by-side
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.image_label)
        horizontal_layout.addWidget(self.plot_widget)

        main_layout.addLayout(horizontal_layout)  # Add the horizontal layout to the main layout

        self.setLayout(main_layout)

        # Initial Plot Data (you can update this later)
        self.plot_trajectory([random.randint(0, 100) for _ in range(50)],
                             [random.randint(0, 100) for _ in range(50)])

        button_layout = QHBoxLayout()

        # Open Video Button
        open_button = QPushButton("Open Video")
        open_button.clicked.connect(self.open_video)
        button_layout.addWidget(open_button)

        # Open CSV Button
        open_csv_button = QPushButton("Load CSV")
        #open_csv_button.clicked.connect(self.load_csv)
        button_layout.addWidget(open_csv_button)


        # Add buttons layout below the video
        main_layout.addLayout(button_layout)

        navigation_layout = QHBoxLayout()

        # Slider for frame navigation
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setEnabled(False)
        #self.slider.sliderMoved.connect(self.slider_changed)
        self.slider.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure the slider can take keyboard focus
        navigation_layout.addWidget(self.slider)

        # Frame Range Input
        form_layout = QFormLayout()

        # Style sheet for making labels white
        label_style = "QLabel { color : white; }"

        self.min_frame_input = QSpinBox(self)
        self.min_frame_input.setMinimum(0)  # Allow frames starting from 0
        self.min_frame_input.setMaximum(1000000)  # Set a large maximum value
        min_frame_label = QLabel("Min Frame:")
        min_frame_label.setStyleSheet(label_style)  # Set label to white
        form_layout.addRow(min_frame_label, self.min_frame_input)

        self.max_frame_input = QSpinBox(self)
        max_frame_label = QLabel("Max Frame:")
        max_frame_label.setStyleSheet(label_style)  # Set label to white
        form_layout.addRow(max_frame_label, self.max_frame_input)

        set_range_button = QPushButton("Set Frame Range")
        #set_range_button.clicked.connect(self.set_frame_range)
        form_layout.addWidget(set_range_button)

        navigation_layout.addLayout(form_layout)

        # Add navigation layout below the video
        main_layout.addLayout(navigation_layout)

        # Container widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Set focus to the main window for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def load_image(self, image_path):
        """Loads an image from the given path and displays it in the image label."""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"Error: Could not load image from {image_path}")
                self.image_label.setText("Image not found")
                return

            self.image_label.setPixmap(pixmap.scaled(self.image_label.width(),
                                                     self.image_label.height(),
                                                     Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label.setText("Error loading image")

    def plot_trajectory(self, x_coords, y_coords):
        """Plots the trajectory data using the PlotWidget."""
        self.plot_widget.plot_data(x_coords, y_coords)

    def open_video(self):
        try:
            # Open file dialog to select video
            video_file, _ = QFileDialog.getOpenFileName(
                self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
            )
            if video_file:
                self.video_cap = cv2.VideoCapture(video_file)
                if not self.video_cap.isOpened():
                    raise IOError("Could not open video file.")

                self.total_frames = int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.max_frame_input.setMaximum(self.total_frames - 1)
                self.max_frame_input.setValue(self.total_frames - 1)

                self.video_loaded = True
                self.slider.setEnabled(True)
                self.slider.setMinimum(self.min_frame)
                self.slider.setMaximum(self.max_frame)
                self.slider.setValue(self.min_frame)

                # Get video width and height for auto-resize
                self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # Adjust QLabel size to match video resolution
                self.image_label.setFixedSize(self.video_width, self.video_height)

                # Set window size to fit the video resolution properly
                self.resize(
                    self.video_width, self.video_height + 150
                )  # Add some height for the controls

                self.show_frame(self.min_frame)

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Matplotlib figure and axes
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasQTAgg(self.figure)  # FigureCanvasAgg(self.figure)

        # Layout for the plot widget
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot_data(self, x, y):
        """Plots the given x and y data."""
        self.ax.clear()  # Clear previous plot

        self.ax.plot(x, y, marker='o', linestyle='-', color='blue')  # Plot trajectory

        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.ax.set_title("Trajectory Plot")
        self.ax.grid(True)  # Add grid lines

        # Refresh canvas to show the updated plot
        self.canvas.draw_idle()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1500, 1000)  # Set initial window size
    window.show()
    sys.exit(app.exec_())
