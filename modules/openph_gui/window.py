from PyQt5 import QtWidgets, QtGui, QtCore

from openph_gui.setting import DARKMODE_STYLESHEET, IMAGE_DIR


class OpenPHWindow(QtWidgets.QMainWindow):
    def __init__(self, filename=None):  # noqa
        super().__init__()
        self.setWindowTitle("OpenPharmaco")
        self.setWindowIcon(QtGui.QIcon(str(IMAGE_DIR / "favicon.ico")))
        self.setStyleSheet(DARKMODE_STYLESHEET)
        self.menuBar()
        self._filename = filename

    def show(self):
        # Loading image
        splash = self.get_splash()
        splash.show()
        self.init_UI()
        splash.close()
        super().show()

    def get_splash(self):
        print(str(IMAGE_DIR / "OpenPharmaco.png"))
        image = QtGui.QImage(str(IMAGE_DIR / "OpenPharmaco.png"))
        image = image.scaled(
            640, 480, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        pixmap = QtGui.QPixmap.fromImage(image)
        splash = QtWidgets.QSplashScreen(pixmap)
        rect = splash.geometry()
        rect.moveCenter(self.geometry().center())
        splash.move(rect.topLeft())
        return splash

    def init_UI(self):
        self.setup_menu()
        self.setup_widget()

    def setup_widget(self):
        from openph_gui.main_widget import OpenPHWidget

        center = self.geometry().center()
        self.main_widget = OpenPHWidget(self)
        self.main_widget.setMinimumSize(960, 720)
        self.setCentralWidget(self.main_widget)
        self.setMinimumSize(960, 720)
        rect = self.geometry()
        rect.moveCenter(center)
        self.move(rect.topLeft())

        self.main_widget.signal.stateInitial.connect(self.state_initial)
        self.main_widget.signal.stateProteinLoaded.connect(self.state_protein_loaded)
        self.main_widget.signal.stateLigandLoaded.connect(self.state_ligand_loaded)
        self.main_widget.signal.stateModelLoaded.connect(self.state_model_loaded)
        self.main_widget.signal.stateAllStop.connect(self.state_all_stop)
        self.main_widget.setup(self._filename)

    def setup_menu(self):
        from openph_gui import actions

        menubar = self.menuBar()
        self.menu_dict = {}
        filemenu = menubar.addMenu("File")
        self.menu_dict["file.model.open"] = self.add_menu(
            filemenu,
            "Open",
            "Open Pharmacophore Model",
            "Ctrl+O",
            lambda: actions.openModel(self.main_widget),
        )
        self.menu_dict["file.model.save"] = self.add_menu(
            filemenu,
            "Save",
            "Save Pharmacophore Model",
            "Ctrl+S",
            lambda: actions.saveModel(self.main_widget),
        )
        filemenu.addSeparator()

        self.menu_dict["file.pymol.export"] = filemenu.addAction(
            "Export to PyMOL", lambda: actions.exportPyMOL(self.main_widget)
        )
        self.menu_dict["file.pymol.save"] = filemenu.addAction(
            "Save PyMOL Session", lambda: actions.savePyMOLSession(self.main_widget)
        )
        filemenu.addSeparator()

        self.menu_dict["file.clear"] = self.add_menu(
            filemenu,
            "Clear",
            "Clear Session",
            "Ctrl+W",
            lambda: actions.clearSession(self.main_widget),
        )

        helpmenu = menubar.addMenu("Help")
        self.menu_dict["help.open_wiki"] = helpmenu.addAction(
            "Online Wiki", lambda: actions.openWiki(self.main_widget)
        )
        self.menu_dict["help.open_arxiv"] = helpmenu.addAction(
            "Online arXiv Paper", lambda: actions.openPaper(self.main_widget)
        )

    def state_initial(self):
        self.menu_dict["file.model.save"].setEnabled(False)
        self.menu_dict["file.model.open"].setEnabled(True)
        self.menu_dict["file.pymol.save"].setEnabled(False)
        self.menu_dict["file.pymol.export"].setEnabled(False)
        self.menu_dict["file.clear"].setEnabled(False)

    def state_protein_loaded(self):
        self.menu_dict["file.model.save"].setEnabled(False)
        self.menu_dict["file.model.open"].setEnabled(False)
        self.menu_dict["file.pymol.save"].setEnabled(True)
        self.menu_dict["file.pymol.export"].setEnabled(True)
        self.menu_dict["file.clear"].setEnabled(True)

    def state_ligand_loaded(self):
        self.menu_dict["file.model.save"].setEnabled(False)
        self.menu_dict["file.model.open"].setEnabled(False)
        self.menu_dict["file.pymol.save"].setEnabled(True)
        self.menu_dict["file.pymol.export"].setEnabled(True)
        self.menu_dict["file.clear"].setEnabled(True)

    def state_model_loaded(self):
        self.menu_dict["file.model.save"].setEnabled(True)
        self.menu_dict["file.model.open"].setEnabled(False)
        self.menu_dict["file.pymol.save"].setEnabled(True)
        self.menu_dict["file.pymol.export"].setEnabled(True)
        self.menu_dict["file.clear"].setEnabled(True)

    def state_all_stop(self):
        self.menu_dict["file.model.save"].setEnabled(False)
        self.menu_dict["file.model.open"].setEnabled(False)
        self.menu_dict["file.pymol.save"].setEnabled(False)
        self.menu_dict["file.pymol.export"].setEnabled(False)
        self.menu_dict["file.clear"].setEnabled(False)

    def add_menu(self, menu, name, tip, shortcut, trigger):
        action = QtWidgets.QAction(name, self)
        action.setStatusTip(tip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(trigger)
        menu.addAction(action)
        return action
