import os
import uuid

import cv2
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, pyqtSlot, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QFileDialog, \
    QMessageBox, QSpinBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from stepanalyzer.algorithms.algorithm_for_steps import count_steps
from stepanalyzer.image_processing.image_processor import show_frame


def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size) / window_size, mode='same')


class Main_Widget(QWidget):
    def __init__(self):
        super().__init__()

        self.name_video = None
        self.file_name_video = None
        self.video_loaded = False
        self.csv_data = pd.DataFrame()  # дата с траетория движния всех суставов
        self.coordinates = {}  # координаты с траетория движния всех суставов
        self.data_angels = []  # многомерный массив со всеми данными углов
        self.data_angels_movmean = []  # array with step marks
        self.result_csv_data = []  # все записи связанные заданными параметрами
        self.local_result_data = []
        self.video_cap = None
        self.current_frame = 0
        self.data_csv_columns = ['id', 'Group', 'Number Rat', 'Name video', 'Step Distance',
                                 'Angle Distance', 'Average Time', 'Average Distance', 'Average Angele']
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

        self.open_video_button = QPushButton("Open Video")
        self.open_csv_trajectory_button = QPushButton("Open CSV trajectory")
        self.open_csv_button = QPushButton("Open CSV angels")
        self.next_button = QPushButton("Next")
        self.back_button = QPushButton("Back")
        self.apply_update_button = QPushButton("Apply Params")
        self.save_to_csv_button = QPushButton("Save Result")

        # Widget for video
        self.image_label = QLabel()

        # Widget for plot
        self.figure = Figure(figsize=(4, 3), dpi=80)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Slider for frame navigation
        self._change_frame_slider = QSlider(Qt.Horizontal)
        self.spinbox_step = QSpinBox()
        self.spinbox_step.setMaximum(200)
        self.spinbox_angle = QSpinBox()
        self.spinbox_step.setMaximum(200)

        # Label for slider
        self.label_count_frame = QLabel()
        self.label_step_distance = QLabel()
        self.label_angle_distance = QLabel()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.setup_UI_widget()

    def setup_UI_widget(self):
        self.image_label.setFixedSize(900, 900)

        self.open_video_button.clicked.connect(self.open_video)
        self.open_csv_trajectory_button.clicked.connect(self.load_csv_data_coordinate)
        self.open_csv_button.clicked.connect(self.load_csv_angles)

        self.spinbox_step.setValue(15)
        self.spinbox_angle.setValue(15)

        self._change_frame_slider.setEnabled(False)
        self.apply_update_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.save_to_csv_button.setEnabled(False)

        self._change_frame_slider.sliderMoved.connect(self.slider_changed)
        self._change_frame_slider.setMinimum(0)
        self._change_frame_slider.setMinimum(1)
        self._change_frame_slider.setValue(0)
        self._change_frame_slider.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure the slider can take keyboard focus

        self.next_button.clicked.connect(self.slider_changed_by_button)
        self.back_button.clicked.connect(self.slider_changed_by_button_back)
        self.apply_update_button.clicked.connect(self.update_params)
        self.save_to_csv_button.clicked.connect(self.save_result_to_csv)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.canvas)

        main_utils_layout = QHBoxLayout()
        buttons_layout_for_video = QVBoxLayout()
        buttons_layout_for_change_frame = QHBoxLayout()
        buttons_layout_for_open_close_frame = QHBoxLayout()

        buttons_layout_for_change_frame.addWidget(self.back_button)
        buttons_layout_for_change_frame.addWidget(self.next_button)

        buttons_layout_for_open_close_frame.addWidget(self.open_video_button)
        buttons_layout_for_open_close_frame.addWidget(self.open_csv_trajectory_button)
        buttons_layout_for_open_close_frame.addWidget(self.open_csv_button)

        buttons_layout_for_video.addLayout(buttons_layout_for_change_frame)
        buttons_layout_for_video.addWidget(self.label_count_frame)
        buttons_layout_for_video.addWidget(self._change_frame_slider)

        main_buttons_for_change_params = QVBoxLayout()
        buttons_for_change_params = QHBoxLayout()

        buttons_for_change_params.addWidget(self.label_step_distance)
        buttons_for_change_params.addWidget(self.spinbox_step)
        buttons_for_change_params.addWidget(self.label_angle_distance)
        buttons_for_change_params.addWidget(self.spinbox_angle)
        buttons_for_change_params.addWidget(self.apply_update_button)
        buttons_for_change_params.addWidget(self.save_to_csv_button)
        main_buttons_for_change_params.addLayout(buttons_layout_for_open_close_frame)
        main_buttons_for_change_params.addLayout(buttons_for_change_params)

        main_utils_layout.addLayout(buttons_layout_for_video, 1)
        main_utils_layout.addLayout(main_buttons_for_change_params, 1)

        # Union up and down layout
        main_widget_layout = QVBoxLayout()
        main_widget_layout.addLayout(image_layout, 1)
        main_widget_layout.addLayout(main_utils_layout, 1)

        self.main_layout.addLayout(main_widget_layout)

        self.label_count_frame.setText('Number Frame')
        self.label_step_distance.setText(f'Step Distance {self.spinbox_step.value()}')
        self.label_angle_distance.setText(f'Angle Distance {self.spinbox_step.value()}')

    def update_params(self):
        self.label_step_distance.setText(f'Step Distance {self.spinbox_step.value()}')
        self.label_angle_distance.setText(f'Angle Distance {self.spinbox_angle.value()}')
        self.local_result_data = []
        self.local_result_data.append(uuid.uuid4())
        self.local_result_data.append(self.file_name_video.split("/")[-2])
        self.local_result_data.append(self.file_name_video.split("_")[-2])
        self.local_result_data.append(self.name_video.split("/")[-1])
        self.local_result_data.append(self.spinbox_step.value())
        self.local_result_data.append(self.spinbox_angle.value())
        if bool(self.result_csv_data) and self.result_csv_data[-1][3] == self.local_result_data[3]:
            self.result_csv_data.pop()
        self.result_csv_data.append(self.local_result_data)

        self.data_angels_movmean.pop()
        self.data_angels_movmean.append(count_steps(self, self.valid_data))

        self.ax.clear()
        self.update_content(self._change_frame_slider.value())

    def update_content(self, position):
        # Обновляем график
        self.ax.clear()
        if position < 60:
            x = np.linspace(0, 120, 120)
            y = self.valid_data[0:120]
            x1 = np.linspace(0, 120, 120)
            y1 = self.data_angels_movmean[3][0:120]

        elif position >= len(self.valid_data) - 120:
            x = np.linspace(len(self.valid_data) - 121, len(self.valid_data) - 1, 120)
            y = self.valid_data[len(self.valid_data) - 121:len(self.valid_data) - 1]
            x1 = np.linspace(len(self.valid_data) - 121, len(self.valid_data) - 1, 120)
            y1 = self.data_angels_movmean[3][len(self.valid_data) - 121:len(self.valid_data) - 1]
        else:
            x = np.linspace(position - 60, position + 60, 120)
            y = self.valid_data[position - 60:position + 60]
            x1 = np.linspace(position - 60, position + 60, 120)
            y1 = self.data_angels_movmean[3][position - 60:position + 60]

        self.ax.plot(x, y)
        self.ax.plot(x1, y1)
        self.ax.set_title(
            f"График {self.file_name_video.split("/")[-2]} {self.file_name_video.split("_")[-2]} elbow_collarbone_paw")
        self.ax.axvline(position, -200, 200, c="red", linestyle="--")
        self.canvas.draw()

    def open_video(self):
        try:
            # Open file dialog to select video
            video_file, _ = QFileDialog.getOpenFileName(
                self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)"
            )
            if video_file:
                self.name_video = video_file
                self.local_result_data = []
                self.video_cap = cv2.VideoCapture(video_file)
                if not self.video_cap.isOpened():
                    raise IOError("Could not open video file.")

                self.next_button.setEnabled(True)
                self.back_button.setEnabled(True)

                self.video_loaded = True
                self._change_frame_slider.setEnabled(True)
                self._change_frame_slider.setMinimum(0)
                self._change_frame_slider.setMaximum(int(self.video_cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
                self._change_frame_slider.setValue(0)

                # Get video width and height for auto-resize
                self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                show_frame(self, 0)

                self.ax.clear()
                self.canvas.draw()
                self.valid_data = []
                self.data_angels = []
                self.data_angels_movmean = []

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

    def load_csv_angles(self):
        try:
            # Open file dialog to select CSV file
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv)"
            )
            if csv_file:
                self.file_name_video = csv_file

                self.apply_update_button.setEnabled(True)
                self.save_to_csv_button.setEnabled(True)
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
                    self.valid_data = column_data[~np.isnan(column_data)]
                    # Remove NaN values for calculation
                    self.valid_data = moving_average(self.valid_data, 5)
                    if len(self.valid_data) < self._change_frame_slider.maximum():
                        self._change_frame_slider.setMaximum(len(self.valid_data) - 1)
                    self.data_angels.append(self.valid_data)
                    self.data_angels_movmean.append(count_steps(self, self.valid_data))
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
        except Exception as e:
            self.show_error_message(f"Error loading CSV: {e}")

    def slider_changed(self, position):
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                show_frame(self, position)
                self.update_content(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def slider_changed_by_button(self):
        position = self._change_frame_slider.value() + 1
        self._change_frame_slider.setValue(position)
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                show_frame(self, position)
                self.update_content(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def slider_changed_by_button_back(self):
        position = self._change_frame_slider.value() - 1
        self._change_frame_slider.setValue(position)
        try:
            # Display the frame corresponding to the slider's position
            if self.video_loaded:
                show_frame(self, position)
                self.update_content(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def keyPressEvent(self, event):
        """Handle key press events for the slider navigation."""
        if event.key() == Qt.Key_Right:  # Right arrow key
            new_value = self._change_frame_slider.value() + 1
            if new_value <= self._change_frame_slider.maximum():
                self._change_frame_slider.setValue(new_value)
                show_frame(self, new_value)
                self.update_content(new_value)
        elif event.key() == Qt.Key_Left:  # Left arrow key
            new_value = self._change_frame_slider.value() - 1
            if new_value >= self._change_frame_slider.minimum():
                self._change_frame_slider.setValue(new_value)
                show_frame(self, new_value)
                self.update_content(new_value)
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

    def save_result_to_csv(self):
        try:
            # Open file dialog to select video
            video_file, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
            if video_file:
                pd.DataFrame(self.result_csv_data, columns=self.data_csv_columns).to_csv(video_file)
        except Exception as e:
            self.show_error_message(f"Error saving CSV: {e}")

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()
