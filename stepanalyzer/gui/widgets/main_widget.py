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

        self.open_video_button = QPushButton("Open Video")
        self.open_video_button.clicked.connect(self.open_video)

        self.open_csv_trajectory_button = QPushButton("Open CSV trajectory")
        self.open_csv_trajectory_button.clicked.connect(self.load_csv_data_coordinate)

        self.open_csv_button = QPushButton("Open CSV angels")
        self.open_csv_button.clicked.connect(self.load_csv_angles)

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
        figure_layout.addWidget(self.image_label)
        figure_layout.addWidget(self.canvas)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addWidget(self.next_button)

        buttons_video_layout = QHBoxLayout()
        buttons_video_layout.addWidget(self.open_video_button)
        buttons_video_layout.addWidget(self.open_csv_trajectory_button)
        buttons_video_layout.addWidget(self.open_csv_button)

        slider_layout = QVBoxLayout()
        slider_layout.addLayout(figure_layout)
        slider_layout.addLayout(buttons_layout)
        slider_layout.addLayout(buttons_video_layout)
        slider_layout.addWidget(self._change_frame_slider)
        slider_layout.addWidget(self.label_count_frame)
        slider_layout.addWidget(self._change_step_slider)
        slider_layout.addWidget(self.label_step_distance)
        slider_layout.addWidget(self._change_angle_slider)
        slider_layout.addWidget(self.label_angle_distance)

        self.main_layout.addLayout(slider_layout)

    def text_changed(self, s):
        self.combo_text = s
        self.update_content(self.slider.value())

    def index_changed(self, index):
        self.combo_index = index
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        if self.combo_index != 4:
            column_data = self.data_angels[self.combo_index]
            column_data = np.array(column_data)
            column_data = column_data.astype(np.float64)
            self.valid_data = column_data[~np.isnan(column_data)]
            self.data_angels_movmean = np.zeros(len(self.valid_data))
            self.count_steps(self.valid_data)
            print(self.data_angels_movmean)
            self.update_content(self.slider.value())
        else:
            self.ax = self.figure.add_subplot(411)
            self.bx = self.figure.add_subplot(412)
            self.cx = self.figure.add_subplot(413)
            self.dx = self.figure.add_subplot(414)
            self.build_three_plots(self.slider.value())

    def update_content(self, position):
        # Обновляем график
        self.ax.clear()
        point = 0
        if position < 60:
            x = np.linspace(0, 120, 120)
            y = self.valid_data[0:120]

        else:
            x = np.linspace(position - 60, position + 60, 120)
            y = self.valid_data[position - 60:position + 60]

        self.ax.plot(x, y)
        self.ax.set_title(f"График {self.combo_text}")
        self.ax.axvline(position, -200, 200, c="red", linestyle="--")
        self.canvas.draw()

    def build_three_plots(self, position):
        self.ax.clear()
        self.bx.clear()
        self.cx.clear()
        self.dx.clear()

        self.ax.set_title(f"График elbow_collarbone_paw")
        self.bx.set_title(f"График hip_iliac_crest_knee")
        self.cx.set_title(f"График knee_hip_ankle")
        self.dx.set_title(f"График ankle_knee_mtp")

        if position < 60:
            self.ax.plot(np.linspace(0, 120, 120), self.data_angels[0][0:120])
            self.bx.plot(np.linspace(0, 120, 120), self.data_angels[1][0:120])
            self.cx.plot(np.linspace(0, 120, 120), self.data_angels[2][0:120])
            self.dx.plot(np.linspace(0, 120, 120), self.data_angels[3][0:120])

        else:
            self.ax.plot(np.linspace(position - 60, position + 60, 120),
                         self.data_angels[0][position - 60:position + 60])
            self.bx.plot(np.linspace(position - 60, position + 60, 120),
                         self.data_angels[1][position - 60:position + 60])

            self.cx.plot(np.linspace(position - 60, position + 60, 120),
                         self.data_angels[2][position - 60:position + 60])
            self.dx.plot(np.linspace(position - 60, position + 60, 120),
                         self.data_angels[3][position - 60:position + 60])

        self.ax.axvline(position, -200, 200, c="red")
        self.bx.axvline(position, -200, 200, c="red")
        self.cx.axvline(position, -200, 200, c="red")
        self.dx.axvline(position, -200, 200, c="red")
        self.canvas.draw()

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

                self.ax.clear()
                self.canvas.draw()
                self.valid_data = []

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

    def load_csv_angles(self):
        try:
            # Open file dialog to select CSV file
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv)"
            )
            if csv_file:
                # Load CSV with pandas

                data_init = np.loadtxt(os.path.join(
                    csv_file),
                    delimiter=',', dtype=str)
                data = data_init[1:]
                data = data.astype(np.float64)
                for i in range(0, 4):
                    column_data = data[0:, i]
                    column_data = np.array(column_data)
                    column_data = column_data.astype(np.float64)
                    self.valid_data = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation
                    self.data_angels.append(self.valid_data)
                    self.data_angels_movmean.append(self.count_steps(self.data_angels))
        except Exception as e:
            self.show_error_message(f"Error loading CSV: {e}")

    def load_csv_data_coordinate(self):
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
        data_init = np.loadtxt(os.path.join(csv_file),
                               delimiter=',', dtype=str)
        data = data_init[1:]
        data = data.astype(np.float64)
        column_data = data[0:, 2]
        column_data = np.array(column_data)
        column_data = column_data.astype(np.float64)

        self.data_coordinates = column_data[~np.isnan(column_data)]  # Remove NaN values for calculation

    def show_frame(self, frame_number):
        try:
            # Set the frame position in the video and read it
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            success, frame = self.video_cap.read()

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
                if not self.csv_data.empty and frame_number in self.csv_data['coords'].values:
                    row_data = self.csv_data[self.csv_data['coords'] == frame_number]

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

                scale_percent = 45
                width = int(frame.shape[1] * scale_percent / 100)
                height = int(frame.shape[0] * scale_percent / 100)
                dim = (width, height)
                frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

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
                if self.combo_index != 4:
                    self.update_content(position)
                else:
                    self.build_three_plots(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def slider_changed_by_button(self):
        position = self.slider.value() + 1
        self.slider.setValue(position)
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                self.show_frame(position)
                if self.combo_index != 4:
                    self.update_content(position)
                else:
                    self.build_three_plots(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def slider_changed_by_button_back(self):
        position = self.slider.value() - 1
        self.slider.setValue(position)
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                self.show_frame(position)
                if self.combo_index != 4:
                    self.update_content(position)
                else:
                    self.build_three_plots(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def keyPressEvent(self, event):
        """Handle key press events for the slider navigation."""
        if event.key() == Qt.Key_Right:  # Right arrow key
            new_value = self.slider.value() + 1
            if new_value <= self.max_frame:
                self.slider.setValue(new_value)
                self.show_frame(new_value)
                if self.combo_index != 4:
                    self.update_content(new_value)
                else:
                    self.build_three_plots(new_value)
        elif event.key() == Qt.Key_Left:  # Left arrow key
            new_value = self.slider.value() - 1
            if new_value >= self.min_frame:
                self.slider.setValue(new_value)
                self.show_frame(new_value)
                if self.combo_index != 4:
                    self.update_content(new_value)
                else:
                    self.build_three_plots(new_value)
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

    def local_extrema_windowed(self, signal, window_size=7, mode='max'):
        half = window_size // 2
        extrema_indices = []

        for i in range(half, len(signal) - half):
            window = signal[i - half:i + half + 1]
            center = signal[i]

            if mode == 'max' and center == np.max(window):
                extrema_indices.append(i)
            elif mode == 'min' and center == np.min(window):
                extrema_indices.append(i)

        return extrema_indices

    def count_steps(self, local_data):
        peaks_max = self.local_extrema_windowed(local_data)

        peaks_min = self.local_extrema_windowed(local_data, mode="min")

        result = []
        temp_array = []
        temp_array.extend(peaks_max)
        temp_array.extend(peaks_min)
        temp_array.sort()
        prev_min = False
        start_step = False

        for i in range(0, len(temp_array)):
            if not start_step and not prev_min and temp_array[i] in peaks_max:
                result.append(temp_array[i])
                prev_min = False
                start_step = True
            elif start_step and not prev_min:
                if temp_array[i] in peaks_min:
                    if abs(local_data[temp_array[i]] - local_data[result[-1]]) > 15:
                        result.append(temp_array[i])
                        prev_min = True
                    else:
                        result.pop()
                        start_step = False
                elif temp_array[i] < result[-1] and not prev_min:
                    result.pop()
                    result.append(temp_array[i])
            elif start_step and prev_min and temp_array[i] in peaks_max:
                if result[-1] - temp_array[i] < 10:
                    result.append(temp_array[i])
                    start_step = False
                else:
                    result.pop()
                    result.pop()
                    result.append(temp_array[i])
                    start_step = True
                prev_min = False
        for i in range(0, len(result), 2):
            self.data_angels_movmean[i] = self.valid_data[i]
        return result

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()


