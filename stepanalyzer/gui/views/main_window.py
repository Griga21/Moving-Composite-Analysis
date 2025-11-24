import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu

from stepanalyzer.gui.widgets.Menu_Widget import Menu_Widget


class Main_GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self._menu_bar = self.menuBar()
        self._file_menu = QMenu('Файл', self)
        self._edit_menu = QMenu('Изменить', self)
        self._help_menu = QMenu('Помощь', self)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Step Analyzer")
        # Icon
        res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources/icon")
        QApplication.instance().setWindowIcon(
            QIcon(os.path.join(res_path, "logo.ico")))

        self.reopen_main_window()
        self._menu_bar.addMenu(self._file_menu)
        self._menu_bar.addMenu(self._edit_menu)
        self._menu_bar.addMenu(self._help_menu)

    def reopen_main_window(self):
        self.setCentralWidget(Menu_Widget(self))
