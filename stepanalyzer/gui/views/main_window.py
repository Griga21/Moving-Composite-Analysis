import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QDesktopWidget, QApplication
from stepanalyzer.gui.widgets.main_widget import Main_Widget


class Main_GUI(QMainWindow):
    def __init__(self):
        super().__init__()

    def setupUI(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle("Step Analyzer")
        self.setGeometry(400, 50, 200, 200)

        # Icon
        res_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "..", "resources")
        QApplication.instance().setWindowIcon(
            QIcon(os.path.join(res_path, "logo.ico")))

        container = Main_Widget()
        self.setCentralWidget(container)
        # self.setFocusPolicy(Qt.StrongFocus)
        # self.setFocus()

        # Menu Bar
        self._menu_bar = self.menuBar()
        file_menu = self._menu_bar.addMenu('&File')
        edit_menu = self._menu_bar.addMenu('&Edit')
        help_menu = self._menu_bar.addMenu('&Help')
