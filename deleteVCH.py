import os
import sys

import cv2
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, \
    QMessageBox
from PyQt5.QtGui import QPixmap, QImage
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image


class ImageGraphApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Смена изображения и графика")
        self.setGeometry(100, 100, 800, 400)

        self.image_index = 0

        self.setWindowTitle("Video Frame Viewer")
        self.setGeometry(200, 200, 800, 600)

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

        # Создаём изображения numpy (прямо в коде)
        self.image_data = [
            np.full((1200, 1300, 3), [255, 0, 0], dtype=np.uint8),  # Красное
            np.full((1200, 1300, 3), [0, 0, 255], dtype=np.uint8)  # Синее
        ]

        # Виджет для изображения
        self.image_label = QLabel()
        self.image_label.setFixedSize(900, 900)

        # Виджет для графика
        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        self.slider = QSlider(Qt.Horizontal)
        # Slider for frame navigation

        self.slider.setEnabled(False)
        self.slider.sliderMoved.connect(self.slider_changed)
        self.slider.setMinimum(0)
        self.slider.setMinimum(1)
        self.slider.setValue(0)
        self.slider.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure the slider can take keyboard focus
        self.setFocus()

        # Кнопка
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.slider_changed_by_button)

        self.back_button = QPushButton("Back")

        self.open_video_button = QPushButton("Open Video")
        self.open_video_button.clicked.connect(self.open_video)

        self.open_csv_button = QPushButton("Open CSV")
        self.open_csv_button.clicked.connect(self.read_data("./","SCI_3_dpi_1_angles.csv"))

        # Layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.image_label)
        h_layout.addWidget(self.canvas)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.next_button)

        buttons_video_layout = QHBoxLayout()
        buttons_video_layout.addWidget(self.open_video_button)
        buttons_video_layout.addWidget(self.open_csv_button)

        navigation_layout = QHBoxLayout()
        navigation_layout.addWidget(self.slider)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addLayout(navigation_layout)
        v_layout.addLayout(buttons_layout)
        v_layout.addLayout(buttons_video_layout)

        self.setLayout(v_layout)

        # Первый вызов
        # self.update_content()

    def update_content(self):
        # Обновляем изображение
        img_array = self.image_data[self.image_index]
        h, w, ch = img_array.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_array.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.image_label.setPixmap(pixmap)

        # Обновляем график
        self.ax.clear()
        x = np.linspace(0, 50, 100)
        y = np.sin(x) if self.image_index == 0 else np.cos(x)
        self.ax.plot(x, y)
        self.ax.set_title(f"График #{self.image_index + 1}")

        self.canvas.draw()

        # Переключение
        self.image_index = (self.image_index + 1) % 2

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
                self.max_frame = self.total_frames - 1

                self.video_loaded = True
                self.slider.setEnabled(True)
                self.slider.setMinimum(0)
                self.slider.setMaximum(self.max_frame)
                self.slider.setValue(0)

                # Get video width and height for auto-resize
                self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                self.show_frame(0)

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

    def read_data(cond_dir, fname):
        """Reads rotation angles and magnitudes, handling potential errors."""
        try:
            data = np.loadtxt(os.path.join(cond_dir, fname), delimiter=',', dtype=str)  # Assuming CSV with commas
            magnitudes_fname = fname[:-10] + 'magnitudes.csv'  # Removing the _angles part
            tbl = np.loadtxt(os.path.join(cond_dir, magnitudes_fname), delimiter=',',
                             dtype=str)  # Assuming CSV with commas
            return data, tbl
        except (FileNotFoundError, ValueError) as e:
            print(f"Error reading {e}")
            return None, None

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

    def show_frame(self, frame_number):
        try:
            # Set the frame position in the video and read it
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = self.video_cap.read()
            scale_percent = 45
            width = int(frame.shape[1] * scale_percent / 100)
            height = int(frame.shape[0] * scale_percent / 100)
            dim = (width, height)
            frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

            if success:
                # Overlay the frame number in the upper right corner
                text = f"Frame: {frame_number}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                color = (255, 255, 255)  # White text
                thickness = 2
                text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
                text_x = self.video_width - text_size[0] - 10  # 10 pixels from the right edge
                text_y = 30  # 30 pixels from the top
                cv2.putText(frame, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

                # If CSV data is available, plot the dots and connect them
                if not self.csv_data.empty and frame_number in self.csv_data['frame'].values:
                    row_data = self.csv_data[self.csv_data['frame'] == frame_number]

                    # List of points to connect with lines (order: crest -> hip -> knee -> ankle -> mtp -> toe)
                    key_points = ['iliaccrest', 'hip', 'knee', 'ankle', 'mtp', 'toe']
                    points = []

                    for index, (label, (x_col, y_col)) in enumerate(self.coordinates.items()):
                        if label in key_points:
                            x = int(float(str(row_data[x_col].values[0]).replace(u'\xa0', u'')))
                            y = int(float(str(row_data[y_col].values[0]).replace(u'\xa0', u'')))
                            points.append((x, y))  # Add the point to the list

                            # Draw the dot (adjust for OpenCV's coordinate system)
                            color = self.colors[index % len(self.colors)]
                            cv2.circle(frame, (x, y), 10, color, -1)

                            # Draw the label text next to the dot
                            label_x = x + 10  # Offset the label slightly
                            label_y = y - 10
                            cv2.putText(frame, label, (label_x, label_y), font, 0.7, color, 2)

                    # Connect the points with lines
                    for i in range(len(points) - 1):
                        start_point = points[i]
                        end_point = points[i + 1]
                        cv2.line(frame, start_point, end_point, (0, 255, 255), 2)  # Yellow line with thickness 2

                # Convert the frame to QImage format and display it
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                qimg = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(qimg))


        except Exception as e:
            self.show_error_message(f"Error showing frame: {e}")

    def slider_changed(self, position):
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                self.show_frame(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def slider_changed_by_button(self):
        position = self.slider.value() + 1
        self.slider.setValue(position)
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                self.show_frame(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def keyPressEvent(self, event):
        """Handle key press events for the slider navigation."""
        if event.key() == Qt.Key_Right:  # Right arrow key
            new_value = self.slider.value() + 1
            if new_value <= self.max_frame:
                self.slider.setValue(new_value)
                self.show_frame(new_value)
        elif event.key() == Qt.Key_Left:  # Left arrow key
            new_value = self.slider.value() - 1
            if new_value >= self.min_frame:
                self.slider.setValue(new_value)
                self.show_frame(new_value)
        else:
            super().keyPressEvent(event)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def closeEvent(self, event):
        if self.video_cap:
            self.video_cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageGraphApp()
    window.show()
    sys.exit(app.exec_())
