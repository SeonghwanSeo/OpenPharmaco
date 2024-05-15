import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from pmgui.window import PMGUIWindow
from pmgui.setting import IMAGE_DIR


def main():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("PharmacoGUI")
    app.setWindowIcon(QtGui.QIcon(QtGui.QIcon(str(IMAGE_DIR / 'favicon.ico'))))
    if len(sys.argv) > 1:
        ex = PMGUIWindow(sys.argv[1])
    else:
        ex = PMGUIWindow()
    ex.show()
    sys.exit(app.exec_())


def run():
    if os.name == 'nt':
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
        os.system(f'_pmgui {" ".join(sys.argv[1:])} > NUL')
    else:
        os.system(f'_pmgui {" ".join(sys.argv[1:])} > /dev/null')


if __name__ == '__main__':
    main()
