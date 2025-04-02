import os
import sys
import random

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image and Trajectory Plot")

        # 1. Image Label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.load_image("your_image.png")  # Replace with your image path

        # 2. Plot Widget (using Matplotlib and FigureCanvas)
        self.plot_widget = PlotWidget()

        # 3. Layout
        main_layout = QVBoxLayout()

        # Create a horizontal layout to hold the image and plot side-by-side
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.image_label)
        horizontal_layout.addWidget(self.plot_widget)

        main_layout.addLayout(horizontal_layout)# Add the horizontal layout to the main layout

        button_layout = QHBoxLayout()
        open_button = QPushButton("Open Video")
        open_button.clicked.connect(self.open_video)
        button_layout.addWidget(open_button)

        # Open CSV Button
        open_csv_button = QPushButton("Load CSV")
        open_csv_button.clicked.connect(self.load_csv)
        button_layout.addWidget(open_csv_button)

        # Add buttons layout below the video
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Initial Plot Data (you can update this later)
        self.plot_trajectory([random.randint(0, 100) for _ in range(30)],
                                [random.randint(0, 100) for _ in range(30)])


    def load_image(self, image_path):
        """Loads an image from the given path and displays it in the image label."""
        try:
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"Error: Could not load image from {image_path}")
                self.image_label.setText("Image not found")
                return

            print(self.image_label.width())
            print(self.image_label.height())
            self.image_label.setPixmap(pixmap.scaled(self.image_label.width()+300,
                                                        self.image_label.height()+100,
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
                self.frame_label.setFixedSize(self.video_width, self.video_height)

                # Set window size to fit the video resolution properly
                self.resize(
                    self.video_width, self.video_height + 150
                )  # Add some height for the controls

                self.show_frame(self.min_frame)

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

    def load_csv(self):
        try:
                # Open file dialog to select CSV file
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv)"
            )
            if csv_file:
                    # Load CSV with pandas
                temp_list = []
                for i in range(19, 39):
                    if i % 3 == 0:
                        continue
                    temp_list.append(i)
                temp_list.append(0)
                temp_list.sort()
                self.csv_data = pd.read_csv(csv_file, usecols=temp_list)

                    # Parse columns and identify pairs of x, y coordinates
                self.coordinates = {}
                columns = self.csv_data.columns

                for i in range(1, len(columns), 2):  # Skip 'frame' column (0 index)
                    if "x" in columns[i].lower() and "y" in columns[i + 1].lower():
                        label = columns[i].lower().replace("_", "").replace("x", "").strip()
                        self.coordinates[label] = (columns[i], columns[i + 1])

                print("Detected Coordinates Pairs:", self.coordinates)
        except Exception as e:
            self.show_error_message(f"Error loading CSV: {e}")
        data_init = np.loadtxt(os.path.join('Intact',
                                                'Intact_1_angles.csv'),
                                   delimiter=',', dtype=str)
        data = data_init[1:]
        data = data.astype(np.float64)
        column_data = data[0:, 2]
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)

        valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111)
        line1, = ax.plot(valid_data, 'b-')

class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create Matplotlib figure and axes
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasQTAgg(self.figure) #FigureCanvasAgg(self.figure)

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
        self.ax.grid(True) # Add grid lines


        # Refresh canvas to show the updated plot
        self.canvas.draw_idle()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1800, 1200)  # Set initial window size
    window.show()
    sys.exit(app.exec_())