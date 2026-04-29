import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QSlider, QWidget


class Abstract_Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.name_video = None
        self.file_name_video = None
        self.video_loaded = False
        self.csv_data = pd.DataFrame()
        self.coordinates = {}
        self.data_angels = []
        self.data_angels_movmean = []
        self.result_csv_data = []
        self.local_result_data = []
        self.video_cap = None
        self.current_frame = 0
        self.check_auto_mode = False

        self.next_button = QPushButton("Следующий кадр")
        self.back_button = QPushButton("Предыдущий кадр")
        self.apply_update_button = QPushButton("Применить параметры")
        self.add_result_to_ram_button = QPushButton("Добавить результат")
        self.apply_update_button.setObjectName("primaryButton")

        self._change_frame_slider = QSlider(Qt.Horizontal)
