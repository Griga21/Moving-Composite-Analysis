import uuid

import cv2
import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt, pyqtSlot, QCoreApplication
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, \
    QMessageBox, QSpinBox, QAction, QMenu, QActionGroup
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from stepanalyzer.Algorithms.Open_Field_ALG import calculate_step_result
from stepanalyzer.gui.widgets.Abstract_Widget import Abstract_Widget
from stepanalyzer.image_processing.image_processor import show_frame_open_field


def moving_average(signal, window_size):
    return np.convolve(signal, np.ones(window_size) / window_size, mode='same')


class Open_Field_Widget(Abstract_Widget):
    def __init__(self, window):
        super().__init__()

        self.name_csv_file = None
        self.window = window
        self.data_csv_columns = ['id', 'Group', 'Number Rat', 'Name video']
        self.results_df = None
        self.stat_tabl = []
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

        # Widget for video
        self.image_label = QLabel()

        # Widget for plot
        self.figure = Figure(figsize=(4, 3), dpi=80)
        self.figure.subplots_adjust(hspace=0.5)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(321)
        self.bx = self.figure.add_subplot(322)
        self.cx = self.figure.add_subplot(323)
        self.dx = self.figure.add_subplot(324)
        self.ex = self.figure.add_subplot(325)
        self.fx = self.figure.add_subplot(326)
        self.set_title_axs()

        self.vline_ax = None
        self.vline_bx = None
        self.vline_cx = None
        self.vline_dx = None
        self.vline_ex = None
        self.vline_fx = None

        # Slider for frame navigation
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

        # Label for slider
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
        self._change_frame_slider.setMinimum(1)
        self._change_frame_slider.setValue(0)
        self._change_frame_slider.setFocusPolicy(
            Qt.StrongFocus
        )  # Ensure the slider can take keyboard focus

        self.next_button.clicked.connect(self.slider_changed_by_button)
        self.back_button.clicked.connect(self.slider_changed_by_button_back)
        self.apply_update_button.clicked.connect(self.update_params)
        self.add_result_to_ram_button.clicked.connect(self.add_RAM_result)

        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.canvas)

        main_utils_layout = QHBoxLayout()
        buttons_layout_for_video = QVBoxLayout()
        buttons_layout_for_change_frame = QHBoxLayout()
        buttons_layout_for_open_close_frame = QHBoxLayout()

        buttons_layout_for_change_frame.addWidget(self.back_button)
        buttons_layout_for_change_frame.addWidget(self.next_button)

        buttons_layout_for_video.addLayout(buttons_layout_for_change_frame)
        buttons_layout_for_video.addWidget(self.label_count_frame)
        buttons_layout_for_video.addWidget(self._change_frame_slider)

        main_buttons_for_change_params = QVBoxLayout()
        buttons_for_change_params = QHBoxLayout()

        buttons_for_change_params.addWidget(self.label_step_distance)
        buttons_for_change_params.addWidget(self.speed_change_min)
        buttons_for_change_params.addWidget(self.speed_change_max)
        buttons_for_change_params.addWidget(self.label_angle_distance)
        buttons_for_change_params.addWidget(self.travel_time_min)
        buttons_for_change_params.addWidget(self.travel_time_max)
        buttons_for_change_params.addWidget(self.apply_update_button)
        buttons_for_change_params.addWidget(self.add_result_to_ram_button)
        main_buttons_for_change_params.addLayout(buttons_layout_for_open_close_frame)
        main_buttons_for_change_params.addLayout(buttons_for_change_params)

        main_utils_layout.addLayout(buttons_layout_for_video, 1)
        main_utils_layout.addLayout(main_buttons_for_change_params, 1)

        # Union up and down layout
        main_widget_layout = QVBoxLayout()
        main_widget_layout.addLayout(image_layout, 1)
        main_widget_layout.addLayout(main_utils_layout, 1)

        self.main_layout.addLayout(main_widget_layout)

        self.label_count_frame.setText('Номер кадра')
        self.label_step_distance.setText(
            f'Изменение скорости {self.speed_change_min.value()} - {self.speed_change_max.value()}')
        self.label_angle_distance.setText(
            f'Интервал передвижения {self.travel_time_min.value()} - {self.travel_time_max.value()}')

    def add_RAM_result(self):
        self.local_result_data = []
        self.local_result_data.append(uuid.uuid4())
        strl = self.name_csv_file.split("/")[-1]

        strl = strl.split(".")[0]
        if len(strl.split("_")) <= 3:
            self.local_result_data.append(strl.split("_")[0])
            self.local_result_data.append(strl.split("_")[-1])
        elif len(strl.split("_")) <= 4:
            self.local_result_data.append(f'{strl.split("_")[0]}_{strl.split("_")[1]}')
            self.local_result_data.append({strl.split("_")[-1]})
        else:
            self.local_result_data.append(f'{strl.split("_")[0]}_{strl.split("_")[1]}_{strl.split("_")[2]}')
            self.local_result_data.append({strl.split("_")[-1]})
        self.local_result_data.append(self.name_video.split("/")[-1])
        for i in range(0, 32):
            self.local_result_data.append(self.stat_tabl[i])

        self.result_csv_data.append(self.local_result_data)

    def update_content(self, position):
        if self.vline_ax is not None:
            self.vline_ax.remove()
            self.vline_bx.remove()
            self.vline_cx.remove()
            self.vline_dx.remove()
            self.vline_ex.remove()
            self.vline_fx.remove()
        self.set_title_axs()

        self.ax.plot()
        self.bx.plot()
        self.cx.plot()
        self.dx.plot()
        self.ex.plot()
        self.fx.plot()

        if position < 30:
            x_limits = (0, 60)
        else:
            x_limits = (position - 30, position + 30)

        for axis in (self.ax, self.bx, self.cx, self.dx, self.ex, self.fx):
            axis.set_xlim(*x_limits)

        self.vline_ax = self.ax.axvline(position, -200, 200, c="red", linestyle="--")
        self.vline_bx = self.bx.axvline(position, -200, 200, c="red", linestyle="--")
        self.vline_cx = self.cx.axvline(position, -200, 200, c="red", linestyle="--")
        self.vline_dx = self.dx.axvline(position, -200, 200, c="red", linestyle="--")
        self.vline_ex = self.ex.axvline(position, -200, 200, c="red", linestyle="--")
        self.vline_fx = self.fx.axvline(position, -200, 200, c="red", linestyle="--")
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

                show_frame_open_field(self, 0)

                self.clear_axs()
                self.set_title_axs()
                self.canvas.draw()
                self.valid_data = []
                self.data_angels = []
                self.data_angels_movmean = []

        except Exception as e:
            self.show_error_message(f"Error loading video: {e}")

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
        self._change_frame_slider.setValue(position)
        self._show_frame_at_position(position)

    def keyPressEvent(self, event):
        """Handle key press events for the slider navigation."""
        if event.key() == Qt.Key_Right:  # Right arrow key
            new_value = self._change_frame_slider.value() + 1
            if new_value <= self._change_frame_slider.maximum():
                self._change_frame_slider.setValue(new_value)
                self._show_frame_at_position(new_value)
        elif event.key() == Qt.Key_Left:  # Left arrow key
            new_value = self._change_frame_slider.value() - 1
            if new_value >= self._change_frame_slider.minimum():
                self._change_frame_slider.setValue(new_value)
                self._show_frame_at_position(new_value)
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
        metrics = ['Median stride time', 'Mean stride time', 'Kvar stride time', 'Frac stride time',
                   'Median stride intl', 'Mean stride intl', 'Kvar stride intl', 'Frac stride intl']
        try:
            file, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
            if file:
                for i in range(4):  # Для каждой лапы
                    for metric in metrics:
                        self.data_csv_columns.append(f'Paw_{i + 1}_{metric}')
                pd.DataFrame(self.result_csv_data, columns=self.data_csv_columns).to_csv(file)
            print("Анализ завершен. Результаты сохранены в movement_analysis_results.csv")
        except Exception as e:
            print(f"Ошибка при сохранении результатов: {e}")

    def add_menu_bar_functional(self):
        bar_open_video_file = QAction('Открыть видео', self)
        bar_open_video_file.triggered.connect(self.open_video)

        bar_open_csv_trajectory = QAction('Открыть CSV траектории', self)
        bar_open_csv_trajectory.triggered.connect(self.load_trajectory_from_csv)

        bar_save_result_to_csv = QAction('Сохранить результаты', self)
        bar_save_result_to_csv.triggered.connect(self.save_result_to_csv)

        self.window._file_menu.addAction(bar_open_video_file)
        self.window._file_menu.addAction(bar_open_csv_trajectory)
        self.window._file_menu.addAction(bar_save_result_to_csv)

        analysis_method_sub_menu = QMenu('Метод анализа', self)
        method_group = QActionGroup(self)  # Group for radio buttons

        manual_method = QAction('Ручной', self, checkable=True)
        manual_method.setActionGroup(method_group)
        manual_method.triggered.connect(self.change_analysis_method_to_manual)
        manual_method.setChecked(True)  # Default selected

        auto_method = QAction('Автоматический', self, checkable=True)
        auto_method.setActionGroup(method_group)
        auto_method.triggered.connect(self.change_analysis_method_to_auto)

        analysis_method_sub_menu.addAction(manual_method)
        analysis_method_sub_menu.addAction(auto_method)
        self.window._edit_menu.addMenu(analysis_method_sub_menu)

        return_main_panel = QAction('Главное меню', self)
        return_main_panel.triggered.connect(self.window.reopen_main_window)
        self.window._edit_menu.addAction(return_main_panel)

    def change_analysis_method_to_manual(self):
        self.check_auto_mode = False
        self.clear_axs()
        self.stat_tabl = []
        self.stat_tabl = calculate_step_result(self, [self.ax, self.bx, self.cx, self.dx, self.ex, self.fx],
                                               self.check_auto_mode)
        self.apply_update_button.setEnabled(True)
        self.speed_change_min.setEnabled(True)
        self.speed_change_max.setEnabled(True)
        self.travel_time_min.setEnabled(True)
        self.travel_time_max.setEnabled(True)

    def change_analysis_method_to_auto(self):
        self.check_auto_mode = True
        self.clear_axs()
        self.stat_tabl = []
        self.stat_tabl = calculate_step_result(self, [self.ax, self.bx, self.cx, self.dx, self.ex, self.fx],
                                               self.check_auto_mode)
        self.apply_update_button.setEnabled(False)
        self.speed_change_min.setEnabled(False)
        self.speed_change_max.setEnabled(False)
        self.travel_time_min.setEnabled(False)
        self.travel_time_max.setEnabled(False)

    def load_trajectory_from_csv(self):
        try:
            # Open file dialog to select CSV file
            csv_file, _ = QFileDialog.getOpenFileName(
                self, "Open CSV File", "", "CSV Files (*.csv)"
            )
            if csv_file:
                self.name_csv_file = csv_file
                # Load CSV with pandas
                temp_list = ["bodyparts", "leftforword_x", "leftforword_y",
                             "rightforword_x", "rightforword_y",
                             "midbody_x", "midbody_y",
                             "leftback_x", "leftback_y",
                             "leftknee_x", "leftknee_y",
                             "rightback_x", "rightback_y",
                             "rightknee_x", "rightknee_y"]

                self.csv_data = pd.read_csv(csv_file, usecols=temp_list)

                # Parse columns and identify pairs of x, y coordinates
                self.coordinates = {}
                columns = self.csv_data.columns

                for i in range(1, len(columns), 2):  # Skip 'frame' column (0 index)
                    if "x" in columns[i].lower() and "y" in columns[i + 1].lower():
                        label = columns[i].lower().replace("_", "").replace("x", "").strip()
                        self.coordinates[label] = (columns[i], columns[i + 1])
                print(self.coordinates)
        except Exception as e:
            self.show_error_message(f"Error loading CSV: {e}")
        self.add_result_to_ram_button.setEnabled(True)
        self.apply_update_button.setEnabled(True)
        self.update_content(0)

    @pyqtSlot()
    def exit_clicked(self):
        self.onClose.emit()
        self.deleteLater()
        self.destroy(True, True)
        QApplication.closeAllWindows()
        QCoreApplication.instance().quit()

    def update_params(self):
        self.label_step_distance.setText(
            f'Изменение скорости {self.speed_change_min.value()} - {self.speed_change_max.value()}')
        self.label_angle_distance.setText(f'Интервал передвижения {self.travel_time_min.value()} '
                                          f'- {self.travel_time_max.value()}')
        self.clear_axs()
        self.stat_tabl = []
        self.stat_tabl = calculate_step_result(self, [self.ax, self.bx, self.cx, self.dx, self.ex, self.fx], self.check_auto_mode)
        self.update_content(self._change_frame_slider.value())

    def set_title_axs(self):
        self.ax.set_title('Передняя левая лапа')
        self.bx.set_title('Передняя правая лапа')
        self.cx.set_title('Задняя левая лапа')
        self.dx.set_title('Задняя правая лапа')
        self.ex.set_title('Левый коленный сустав')
        self.fx.set_title('Правый коленный сустав')

    def clear_axs(self):
        self.ax.clear()
        self.bx.clear()
        self.cx.clear()
        self.dx.clear()
        self.ex.clear()
        self.fx.clear()
