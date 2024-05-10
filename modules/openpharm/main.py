import sys
import os
from pathlib import Path

from PyQt5 import QtWidgets, QtGui, QtCore

import openpharm
from openpharm import actions
from openpharm.openpharm_widget import OpenPharmWidget
from openpharm.setting import DARKMODE_STYLESHEET, IMAGE_DIR


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, filename=None):  # noqa
        super().__init__()
        self.setup_menu()
        self.setWindowTitle('OpenPharmGUI')
        self.setWindowIcon(QtGui.QIcon(str(IMAGE_DIR / 'favicon.ico')))
        self.main_widget = OpenPharmWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setMinimumSize(960, 720)
        self.setMinimumSize(960, 720)
        self.main_widget.signal.stateInitial.connect(self.state_initial)
        self.main_widget.signal.stateProteinLoaded.connect(self.state_protein_loaded)
        self.main_widget.signal.stateLigandLoaded.connect(self.state_ligand_loaded)
        self.main_widget.signal.stateModelLoaded.connect(self.state_model_loaded)
        self.main_widget.signal.stateAllStop.connect(self.state_all_stop)
        self._filename = filename

    def show(self):
        pixmap = QtGui.QPixmap(str(IMAGE_DIR / 'loading_image.png'))
        pixmap = pixmap.scaled(640, 480)
        splash = QtWidgets.QSplashScreen(pixmap)
        rect = splash.geometry()
        rect.moveCenter(self.geometry().center())
        splash.move(rect.topLeft())
        splash.show()
        if self._filename is not None:
            self.main_widget.setup(self._filename)
        else:
            self.main_widget.setup()
        splash.close()
        super().show()

    def setup_menu(self):
        menubar = self.menuBar()
        self.menu_dict = {}
        filemenu = menubar.addMenu('File')
        self.menu_dict['file.model.open'] = filemenu.addAction('Open Pharmacophore Model', lambda: actions.openModel(self.main_widget))
        self.menu_dict['file.model.save'] = filemenu.addAction('Save Pharmacophore Model', lambda: actions.saveModel(self.main_widget))
        self.menu_dict['file.pymol.export'] = filemenu.addAction('Export to PyMOL', lambda: actions.exportPyMOL(self.main_widget))
        self.menu_dict['file.pymol.save'] = filemenu.addAction('Save PyMOL Session', lambda: actions.savePyMOLSession(self.main_widget))

    def state_initial(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(True)
        self.menu_dict['file.pymol.save'].setEnabled(False)
        self.menu_dict['file.pymol.export'].setEnabled(False)

    def state_protein_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)

    def state_ligand_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)

    def state_model_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(True)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)

    def state_all_stop(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(False)
        self.menu_dict['file.pymol.export'].setEnabled(False)


def main():
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OpenPharmGUI")
    app.setWindowIcon(QtGui.QIcon(QtGui.QIcon(str(IMAGE_DIR / 'favicon.ico'))))
    app.setStyleSheet(DARKMODE_STYLESHEET)
    if len(sys.argv) > 1:
        ex = MainApp(sys.argv[1])
    else:
        ex = MainApp()
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
