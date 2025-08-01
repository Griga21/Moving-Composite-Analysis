import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from PyQt5 import QtGui

from stepanalyzer.gui.widgets.Main_Widget import Main_Widget


class Main_GUI(QMainWindow):
    def __init__(self):
        super().__init__()

    def setupUI(self):
        self.setWindowTitle("Step Analyzer")

        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.setGeometry(x,y, 0, 0)

        # Icon
        res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources")
        QApplication.instance().setWindowIcon(
            QIcon(os.path.join(res_path, "logo.ico")))

        container = Main_Widget()
        self.setCentralWidget(container)

        # Menu Bar
        self._menu_bar = self.menuBar()
        file_menu = self._menu_bar.addMenu('&File')
        edit_menu = self._menu_bar.addMenu('&Edit')
        help_menu = self._menu_bar.addMenu('&Help')
