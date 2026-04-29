import math
import os
import uuid

import cv2
import pandas as pd
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSlot
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QMenu,
    QSpinBox,
    QVBoxLayout,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from stepanalyzer.Algorithms.trajectory_utils import (
    point_speed,
    point_summary,
    read_trajectory_csv,
)
from stepanalyzer.gui.widgets.Abstract_Widget import Abstract_Widget
from stepanalyzer.image_processing.image_processor import show_frame_open_field


class Open_Field_Widget(Abstract_Widget):
    def __init__(self, window):
        super().__init__()

        self.name_csv_file = None
        self.frame_column = None
        self.connect_points = True
        self.window = window
        self.data_csv_columns = ["id", "source_file", "point", "mean_x", "mean_y", "mean_speed", "max_speed", "path_length"]
        self.results_df = pd.DataFrame()
        self.stat_tabl = []
        self.axes = []
        self.signal_cache = {}

        self.colors = [
            (255, 0, 0),
            (0, 170, 0),
            (0, 0, 255),
            (255, 190, 0),
            (255, 120, 0),
            (0, 180, 220),
            (220, 0, 220),
            (128, 0, 128),
            (0, 128, 128),
            (128, 128, 0),
            (80, 80, 80),
            (40, 120, 200),
        ]

        self.image_label = QLabel()
        self.figure = Figure(figsize=(6, 4), dpi=80)
        self.figure.subplots_adjust(hspace=0.55, wspace=0.28)
        self.canvas = FigureCanvas(self.figure)

        self.speed_change_min = QSpinBox()
        self.speed_change_min.setMinimum(0)
        self.speed_change_min.setMaximum(1000)
        self.speed_change_max = QSpinBox()
        self.speed_change_max.setMinimum(0)
        self.speed_change_max.setMaximum(1000)
        self.travel_time_min = QSpinBox()
        self.travel_time_min.setMinimum(0)
        self.travel_time_min.setMaximum(1000)
        self.travel_time_max = QSpinBox()
        self.travel_time_max.setMinimum(0)
        self.travel_time_max.setMaximum(1000)

        self.label_count_frame = QLabel()
        self.label_step_distance = QLabel()
        self.label_angle_distance = QLabel()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.setup_UI_widget()
        self.add_menu_bar_functional()

    def setup_UI_widget(self):
        self.image_label.setFixedSize(900, 900)
        self.speed_change_min.setValue(15)
        self.speed_change_max.setValue(50)
        self.travel_time_min.setValue(15)
        self.travel_time_max.setValue(50)

        self._change_frame_slider.setEnabled(False)
        self.apply_update_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.back_button.setEnabled(False)
        self.add_result_to_ram_button.setEnabled(False)

        self._change_frame_slider.sliderMoved.connect(self.slider_changed)
        self._change_frame_slider.setMinimum(0)
        self._change_frame_slider.setValue(0)
        self._change_frame_slider.setFocusPolicy(Qt.StrongFocus)

        self.next_button.clicked.connect(self.slider_changed_by_button)
        self.back_button.clicked.connect(self.slider_changed_by_button_back)
        self.apply_update_button.clicked.connect(self.update_params)
        self.add_result_to_ram_button.clicked.connect(self.add_RAM_result)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.canvas)

        buttons_layout_for_video = QVBoxLayout()
        buttons_layout_for_change_frame = QHBoxLayout()
        buttons_layout_for_change_frame.addWidget(self.back_button)
        buttons_layout_for_change_frame.addWidget(self.next_button)
        buttons_layout_for_video.addLayout(buttons_layout_for_change_frame)
        buttons_layout_for_video.addWidget(self.label_count_frame)
        buttons_layout_for_video.addWidget(self._change_frame_slider)

        buttons_for_change_params = QHBoxLayout()
        buttons_for_change_params.addWidget(self.label_step_distance)
        buttons_for_change_params.addWidget(self.speed_change_min)
        buttons_for_change_params.addWidget(self.speed_change_max)
        buttons_for_change_params.addWidget(self.label_angle_distance)
        buttons_for_change_params.addWidget(self.travel_time_min)
        buttons_for_change_params.addWidget(self.travel_time_max)
        buttons_for_change_params.addWidget(self.apply_update_button)
        buttons_for_change_params.addWidget(self.add_result_to_ram_button)

        main_utils_layout = QHBoxLayout()
        main_utils_layout.addLayout(buttons_layout_for_video, 1)
        main_utils_layout.addLayout(buttons_for_change_params, 1)

        self.main_layout.addLayout(image_layout, 1)
        self.main_layout.addLayout(main_utils_layout, 1)

        self.label_count_frame.setText("Кадр")
        self.label_step_distance.setText("Диапазон скорости")
        self.label_angle_distance.setText("Интервал движения")
        self.rebuild_axes(["Загрузите CSV с координатами"])

    def rebuild_axes(self, labels):
        self.figure.clear()
        labels = labels or ["Нет найденных точек"]
        n_points = len(labels)
        n_cols = 2 if n_points > 1 else 1
        n_rows = math.ceil(n_points / n_cols)
        self.axes = []

        for index, label in enumerate(labels, start=1):
            axis = self.figure.add_subplot(n_rows, n_cols, index)
            axis.set_title(label)
            axis.grid(True, linestyle="--", alpha=0.35)
            self.axes.append(axis)

        self.figure.subplots_adjust(hspace=0.55, wspace=0.28)
        self.canvas.draw()

    def build_signal_cache(self):
        self.signal_cache = {}
        for label, (x_col, y_col) in self.coordinates.items():
            self.signal_cache[label] = point_speed(self.csv_data, x_col, y_col)

    def update_content(self, position):
        if self.csv_data.empty or not self.coordinates:
            self.rebuild_axes(["Загрузите CSV с координатами"])
            return

        labels = list(self.coordinates.keys())
        if len(self.axes) != len(labels):
            self.rebuild_axes(labels)

        frame_values = self.csv_data[self.frame_column].to_numpy()

        for index, label in enumerate(labels):
            axis = self.axes[index]
            axis.clear()
            axis.grid(True, linestyle="--", alpha=0.35)
            axis.set_title(label)
            axis.set_ylabel("coordinate / speed")

            x_col, y_col = self.coordinates[label]
            x_values = self.csv_data[x_col].astype(float).interpolate(limit_direction="both").to_numpy()
            y_values = self.csv_data[y_col].astype(float).interpolate(limit_direction="both").to_numpy()

            speed = self.signal_cache.get(label)
            if speed is None:
                speed = point_speed(self.csv_data, x_col, y_col)
                self.signal_cache[label] = speed

            axis.plot(frame_values, x_values, color="#1f6feb", linewidth=1.4, label="x")
            axis.plot(frame_values, y_values, color="#2ca02c", linewidth=1.4, label="y")
            axis.plot(frame_values, speed, color="#7f3fbf", linewidth=1.0, linestyle="--", label="speed")
            axis.axvline(position, color="#d62728", linestyle="--", linewidth=1.2)

            current_row = self._current_row(position)
            if current_row is not None and not current_row[[x_col, y_col]].isna().any():
                row_index = min(current_row.name, len(speed) - 1)
                axis.scatter(
                    [position, position],
                    [x_values[row_index], y_values[row_index]],
                    color="#d62728",
                    s=22,
                    zorder=3,
                )
            axis.legend(loc="upper right", fontsize=7)

            if position < 30:
                axis.set_xlim(0, max(60, position + 30))
            else:
                axis.set_xlim(position - 30, position + 30)

        self.canvas.draw()

    def _current_row(self, position):
        rows = self.csv_data[self.csv_data[self.frame_column] == position]
        if not rows.empty:
            return rows.iloc[0]

        if 0 <= position < len(self.csv_data):
            return self.csv_data.iloc[position]

        return None

    def open_video(self):
        try:
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

                self.video_width = int(self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.video_height = int(self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                show_frame_open_field(self, 0)
                self.update_content(0)

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

    def load_trajectory_from_csv(self):
        try:
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv)"
            )
            if not csv_file:
                return

            self.name_csv_file = csv_file
            self.csv_data, self.frame_column, self.coordinates = read_trajectory_csv(csv_file)
            self.build_signal_cache()
            self.rebuild_axes(list(self.coordinates.keys()))

            max_frame = int(self.csv_data[self.frame_column].max())
            if self.video_loaded:
                max_frame = min(max_frame, self._change_frame_slider.maximum())
            self._change_frame_slider.setMinimum(int(self.csv_data[self.frame_column].min()))
            self._change_frame_slider.setMaximum(max_frame)
            self._change_frame_slider.setValue(int(self.csv_data[self.frame_column].min()))

            self.add_result_to_ram_button.setEnabled(True)
            self.apply_update_button.setEnabled(True)
            self._change_frame_slider.setEnabled(True)
            self.results_df = point_summary(self.csv_data, self.coordinates)
            self.update_content(self._change_frame_slider.value())

            if self.video_loaded:
                show_frame_open_field(self, self._change_frame_slider.value())

        except Exception as e:
            self.show_error_message(f"Error loading CSV: {e}")

    def slider_changed(self, position):
        self._show_frame_at_position(position)

    def slider_changed_by_button(self):
        self._shift_frame_by(1)

    def slider_changed_by_button_back(self):
        self._shift_frame_by(-1)

    def _show_frame_at_position(self, position):
        try:
            if self.video_loaded:
                show_frame_open_field(self, position)
            self.update_content(position)
        except Exception as e:
            self.show_error_message(f"Error displaying frame: {e}")

    def _shift_frame_by(self, step):
        position = self._change_frame_slider.value() + step
        position = max(self._change_frame_slider.minimum(), min(position, self._change_frame_slider.maximum()))
        self._change_frame_slider.setValue(position)
        self._show_frame_at_position(position)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Right:
            self._shift_frame_by(1)
        elif event.key() == Qt.Key_Left:
            self._shift_frame_by(-1)
        else:
            super().keyPressEvent(event)

    def add_RAM_result(self):
        if self.csv_data.empty or not self.coordinates:
            return

        source_file = os.path.basename(self.name_csv_file or "")
        summary = point_summary(self.csv_data, self.coordinates)
        for _, row in summary.iterrows():
            self.result_csv_data.append(
                [
                    uuid.uuid4(),
                    source_file,
                    row["point"],
                    row["mean_x"],
                    row["mean_y"],
                    row["mean_speed"],
                    row["max_speed"],
                    row["path_length"],
                ]
            )

    def save_result_to_csv(self):
        try:
            file, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
            if not file:
                return

            if self.result_csv_data:
                pd.DataFrame(self.result_csv_data, columns=self.data_csv_columns).to_csv(file, index=False)
            elif not self.csv_data.empty and self.coordinates:
                point_summary(self.csv_data, self.coordinates).to_csv(file, index=False)

        except Exception as e:
            self.show_error_message(f"Error saving CSV: {e}")

    def add_menu_bar_functional(self):
        bar_open_video_file = QAction("Открыть видео", self)
        bar_open_video_file.triggered.connect(self.open_video)

        bar_open_csv_trajectory = QAction("Открыть CSV траектории", self)
        bar_open_csv_trajectory.triggered.connect(self.load_trajectory_from_csv)

        bar_save_result_to_csv = QAction("Сохранить результаты", self)
        bar_save_result_to_csv.triggered.connect(self.save_result_to_csv)

        self.window._file_menu.addAction(bar_open_video_file)
        self.window._file_menu.addAction(bar_open_csv_trajectory)
        self.window._file_menu.addAction(bar_save_result_to_csv)

        analysis_method_sub_menu = QMenu("Метод анализа", self)
        refresh_action = QAction("Перестроить графики", self)
        refresh_action.triggered.connect(self.update_params)
        analysis_method_sub_menu.addAction(refresh_action)
        self.window._edit_menu.addMenu(analysis_method_sub_menu)

        return_main_panel = QAction("Главное меню", self)
        return_main_panel.triggered.connect(self.window.reopen_main_window)
        self.window._edit_menu.addAction(return_main_panel)

    def update_params(self):
        self.results_df = point_summary(self.csv_data, self.coordinates) if self.coordinates else pd.DataFrame()
        self.update_content(self._change_frame_slider.value())

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

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()
