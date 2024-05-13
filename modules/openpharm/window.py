from PyQt5 import QtWidgets, QtGui

import openpharm
from openpharm import actions
from openpharm.widget import OpenPharmWidget
from openpharm.setting import DARKMODE_STYLESHEET, IMAGE_DIR


class OpenPharmWindow(QtWidgets.QMainWindow):
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
        self.setStyleSheet(DARKMODE_STYLESHEET)

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
        self.menu_dict['file.model.open'] = self.add_menu(
            filemenu, 'Open', 'Open Pharmacophore Model', 'Ctrl+O',
            lambda: actions.openModel(self.main_widget)
        )
        self.menu_dict['file.model.save'] = self.add_menu(
            filemenu, 'Save', 'Save Pharmacophore Model', 'Ctrl+S',
            lambda: actions.saveModel(self.main_widget)
        )
        filemenu.addSeparator()

        self.menu_dict['file.pymol.export'] = filemenu.addAction('Export to PyMOL', lambda: actions.exportPyMOL(self.main_widget))
        self.menu_dict['file.pymol.save'] = filemenu.addAction('Save PyMOL Session', lambda: actions.savePyMOLSession(self.main_widget))
        filemenu.addSeparator()

        self.menu_dict['file.clear'] = self.add_menu(
            filemenu, 'Clear', 'Clear Session', 'Ctrl+W',
            lambda: actions.clearSession(self.main_widget)
        )

        helpmenu = menubar.addMenu('Help')
        self.menu_dict['help.open_wiki'] = helpmenu.addAction('Online Wiki', lambda: actions.openWiki(self.main_widget))
        self.menu_dict['help.open_arxiv'] = helpmenu.addAction('Online arXiv Paper', lambda: actions.openPaper(self.main_widget))

    def state_initial(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(True)
        self.menu_dict['file.pymol.save'].setEnabled(False)
        self.menu_dict['file.pymol.export'].setEnabled(False)
        self.menu_dict['file.clear'].setEnabled(False)

    def state_protein_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)
        self.menu_dict['file.clear'].setEnabled(True)

    def state_ligand_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)
        self.menu_dict['file.clear'].setEnabled(True)

    def state_model_loaded(self):
        self.menu_dict['file.model.save'].setEnabled(True)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(True)
        self.menu_dict['file.pymol.export'].setEnabled(True)
        self.menu_dict['file.clear'].setEnabled(True)

    def state_all_stop(self):
        self.menu_dict['file.model.save'].setEnabled(False)
        self.menu_dict['file.model.open'].setEnabled(False)
        self.menu_dict['file.pymol.save'].setEnabled(False)
        self.menu_dict['file.pymol.export'].setEnabled(False)
        self.menu_dict['file.clear'].setEnabled(False)

    def add_menu(self, menu, name, tip, shortcut, trigger):
        action = QtWidgets.QAction(name, self)
        action.setStatusTip(tip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(trigger)
        menu.addAction(action)
        return action