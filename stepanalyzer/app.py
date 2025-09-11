import sys

from PyQt5.QtWidgets import QApplication

from gui.views.main_window import Main_GUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main_GUI()
    window.showMaximized()
    sys.exit(app.exec_())
