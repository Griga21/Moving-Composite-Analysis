import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QSlider


class Abstract_Widget(QWidget):
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
        self.check_auto_mode = False

        self.next_button = QPushButton("Вперед")
        self.back_button = QPushButton("Назад")
        self.apply_update_button = QPushButton("Применить параметры")
        self.add_result_to_ram_button = QPushButton("Добавить результат")

        self._change_frame_slider = QSlider(Qt.Horizontal)
