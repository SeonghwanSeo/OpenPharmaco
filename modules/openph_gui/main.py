import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from openph_gui.window import OpenPHWindow
from openph_gui.setting import IMAGE_DIR


def main():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OpenPharmaco")
    app.setWindowIcon(QtGui.QIcon(QtGui.QIcon(str(IMAGE_DIR / 'favicon.ico'))))
    path = sys.argv[1] if len(sys.argv) > 1 else None
    ex = OpenPHWindow(path)
    ex.show()
    sys.exit(app.exec_())


def run():
    if os.name == 'nt':
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
        os.system(f'_openpharmaco {" ".join(sys.argv[1:])} > NUL')
    else:
        os.system(f'_openpharmaco {" ".join(sys.argv[1:])} > /dev/null')


if __name__ == '__main__':
    main()
