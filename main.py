import sys
import os

from PyQt5 import QtWidgets, QtGui, QtCore

from openpharm.gui import actions
from openpharm.gui import OpenPharmWidget
from openpharm.gui.setting import DARKMODE_STYLESHEET


class MainApp(QtWidgets.QMainWindow):
    def __init__(self, filename=None):  # noqa
        super().__init__()
        self.setup_menu()
        self.setWindowTitle('OpenPharmGUI')
        self.setWindowIcon(QtGui.QIcon('./images/favicon.png'))
        self.main_widget = OpenPharmWidget(self)
        self.setCentralWidget(self.main_widget)
        self.resize(960, 800)
        self.main_widget.signal.stateInitial.connect(self.state_initial)
        self.main_widget.signal.stateProteinLoaded.connect(self.state_protein_loaded)
        self.main_widget.signal.stateLigandLoaded.connect(self.state_ligand_loaded)
        self.main_widget.signal.stateModelLoaded.connect(self.state_model_loaded)
        self.main_widget.signal.stateAllStop.connect(self.state_all_stop)

        self._filename = filename

    def show(self):
        if self._filename is not None:
            assert os.path.splitext(self._filename)[-1] == '.pm', f'Invalid filename ({self._filename}), require `.pm`'
        pixmap = QtGui.QPixmap('./images/loading_image.png')
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


if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("OpenPharmGUI")
    app.setWindowIcon(QtGui.QIcon('./images/favicon.png'))
    app.setStyleSheet(DARKMODE_STYLESHEET)
    if len(sys.argv) > 1:
        ex = MainApp(sys.argv[1])
    else:
        ex = MainApp()
    ex.show()
    sys.exit(app.exec_())
