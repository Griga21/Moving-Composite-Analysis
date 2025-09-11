import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication

from stepanalyzer.gui.widgets.Menu_Widget import Menu_Widget


class Main_GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Step Analyzer")
        # Icon
        res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources/icon")
        QApplication.instance().setWindowIcon(
            QIcon(os.path.join(res_path, "logo.icon")))

        container = Menu_Widget(self)
        self.setCentralWidget(container)

        # Menu Bar
        self._menu_bar = self.menuBar()
        file_menu = self._menu_bar.addMenu('&File')
        edit_menu = self._menu_bar.addMenu('&Edit')
        help_menu = self._menu_bar.addMenu('&Help')
