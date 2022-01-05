from PyQt5 import QtWidgets
import sys
from src import gui
import qdarkstyle


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    vd = gui.MainWindow()
    vd.show()
    sys.excepthook = except_hook
    app.exec_()


if __name__ == '__main__':
    main()