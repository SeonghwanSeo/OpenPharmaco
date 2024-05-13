import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from openpharm.window import OpenPharmWindow
from openpharm.setting import IMAGE_DIR


def main():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OpenPharmGUI")
    app.setWindowIcon(QtGui.QIcon(QtGui.QIcon(str(IMAGE_DIR / 'favicon.ico'))))
    if len(sys.argv) > 1:
        ex = OpenPharmWindow(sys.argv[1])
    else:
        ex = OpenPharmWindow()
    ex.show()
    sys.exit(app.exec_())


def run():
    if os.name == 'nt':
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
        os.system(f'_openpharm {" ".join(sys.argv[1:])} > NUL')
    else:
        os.system(f'_openpharm {" ".join(sys.argv[1:])} > /dev/null')


if __name__ == '__main__':
    main()
