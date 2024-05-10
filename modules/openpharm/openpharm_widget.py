import time
from pathlib import Path
from collections import OrderedDict
from datetime import datetime
import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QObject

import pymol
from pmg_qt.pymol_gl_widget import PyMOLGLWidget
from pmg_qt.pymol_qt_gui import PyMOLGLWidget

from . import actions, objects

from typing import Optional


class OpenPharmSignal(QObject):
    stateInitial = pyqtSignal()
    stateProteinLoaded = pyqtSignal()
    stateLigandLoaded = pyqtSignal()
    stateModelLoaded = pyqtSignal()
    stateAllStop = pyqtSignal()


class OpenPharmWidget(QtWidgets.QWidget):
    def __init__(self, window):  # noqa
        super().__init__()
        self.signal = OpenPharmSignal()
        self.window = window
        self.setAcceptDrops(True)
        self.init_pymol()
        self.setup_layout()
        self.add_widgets()
        self.resize_layout()
        self.state_initial()
        self.protein: Optional[str] = None
        self.protein_path: Optional[str] = None
        self.binding_site: Optional[str] = None
        self.ligand_path_dict: OrderedDict[str, str] = OrderedDict()

    def sizeHint(self):
        return QtCore.QSize(640 + 320, 480 + 240)

    def setup(self, filename=None):
        self._setup_pmnet()
        if filename:
            if os.path.splitext(filename)[-1] == '.pm':
                actions.setup_model(self, filename)
            else:
                self.print_log(f'Invalid filename ({filename}), require `.pm`')

    def _setup_pmnet(self):
        # NOTE: Load PharmacoNet
        st = time.time()
        import openpharm
        from pmnet import PharmacophoreModel
        from pmnet.module import PharmacoNet

        MODULE_PATH = Path(openpharm.__file__).parent.parent
        weight_path = MODULE_PATH / 'weight' / 'model.tar'
        if not weight_path.exists():
            dialog = objects.download_dialog.DownloadDialog(self, weight_path)
            dialog.exec_()
        self.module: PharmacoNet = PharmacoNet(str(weight_path))
        self.pharmacophore_model: Optional[PharmacophoreModel] = None
        self.pharmacophore_model_name: Optional[str] = None
        self.logOutput.appendPlainText(openpharm.__description__)

        end = time.time()
        if (end - st) < 1.5:
            time.sleep(1.5 - (end - st))
        self.print_log('Start OpenPharm GUI')

    def init_pymol(self):
        options = pymol.invocation.options
        options.internal_feedback = False
        options.external_gui = False
        options.internal_gui = False

    def setup_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.ext_layout = QtWidgets.QVBoxLayout()
        self.center_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.ext_layout)
        self.main_layout.addLayout(self.center_layout)

        # NOTE: ext_layout
        self.ext_menu_layout = QtWidgets.QGridLayout()
        self.ext_log_layout = QtWidgets.QHBoxLayout()
        self.ext_layout.addLayout(self.ext_menu_layout)
        self.ext_layout.addLayout(self.ext_log_layout)

    def resize_layout(self):
        self.main_layout.setStretch(0, 5)
        self.main_layout.setStretch(1, 12)
        self.main_layout.setSpacing(5)

        self.ext_layout.setStretch(0, 0)
        self.ext_layout.setStretch(1, 1)
        self.ext_layout.setSpacing(5)
        self.center_layout.setStretch(0, 3)
        self.center_layout.setStretch(1, 8)

    def add_widgets(self):
        # NOTE: Ext Layout
        self.pdbEnter = QtWidgets.QLineEdit(self)
        self.pdbEnter.returnPressed.connect(lambda: actions.loadRCSB(self))
        self.pdbEnter.setPlaceholderText("Enter RCSB PDB Code (ex. 10gs)")
        self.pdbEnter.setMaxLength(4)
        self.pdbEnter.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.pdbEnter, 0, 0, 1, 2)

        self.proteinButton = QtWidgets.QPushButton("Open Protein File", self)
        self.proteinButton.clicked.connect(lambda: actions.openProtein(self))
        self.proteinButton.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.proteinButton, 1, 0, 1, 1)

        self.ligandButton = QtWidgets.QPushButton("Open Ligand File", self)
        self.ligandButton.clicked.connect(lambda: actions.openLigand(self))
        self.ligandButton.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.ligandButton, 1, 1, 1, 1)

        self.modelingButton = QtWidgets.QPushButton("Modeling", self)
        self.modelingButton.clicked.connect(lambda: actions.modeling(self))
        self.modelingButton.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.modelingButton, 0, 2, 1, 2)

        self.loadModelButton = QtWidgets.QPushButton("Open Model File", self)
        self.loadModelButton.clicked.connect(lambda: actions.openModel(self))
        self.loadModelButton.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.loadModelButton, 1, 2, 1, 1)

        self.saveModelButton = QtWidgets.QPushButton("Save Model File", self)
        self.saveModelButton.clicked.connect(lambda: actions.saveModel(self))
        self.saveModelButton.setMaximumHeight(25)
        self.ext_menu_layout.addWidget(self.saveModelButton, 1, 3, 1, 1)

        self.runScreeningButton = QtWidgets.QPushButton("Screening", self)
        self.runScreeningButton.clicked.connect(lambda: actions.openScreening(self))
        self.runScreeningButton.setMaximumHeight(60)
        self.ext_menu_layout.addWidget(self.runScreeningButton, 0, 4, 2, 1)

        self.clearButton = QtWidgets.QPushButton("Clear", self)
        self.clearButton.clicked.connect(lambda: actions.clearSession(self))
        self.clearButton.setMaximumHeight(60)
        self.ext_menu_layout.addWidget(self.clearButton, 0, 5, 2, 1)

        # NOTE: Log Layout
        self.logOutput = QtWidgets.QPlainTextEdit(self)
        self.logOutput.setReadOnly(True)
        self.ext_log_layout.addWidget(self.logOutput)

        # NOTE: Center Layout
        self.treeWidget = objects.explorer.ViewerQTreeWidget(self)
        self.treeWidget.itemClicked.connect(lambda item: item.toggle())
        self.center_layout.addWidget(self.treeWidget)

        self.main_widget = PyMOLGLWidget(self)
        self.main_widget.fb_scale = 2
        self.center_layout.addWidget(self.main_widget)
        pymol.cmd.bg_color('white')
        pymol.cmd.pseudoatom('dummy')
        pymol.cmd.delete('dummy')

    def print_log(self, log):
        currentTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logOutput.appendPlainText(f'{currentTime}> {log}')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    url = url.toLocalFile()
                else:
                    url = url.toString()
                self.load_dialog(url)
            event.accept()

    def load_dialog(self, filename):
        if os.path.splitext(filename)[-1] == '.pm':
            if self.protein is not None:
                actions.clearSession(self)
            actions.setup_model(self, filename)
        else:
            self.print_log(f'Invalid File: {filename}')

    def state_initial(self):
        self.protein = None
        self.protein_path = None
        self.binding_site = None
        self.ligand_path_dict = OrderedDict()
        self.pdbEnter.setEnabled(True)
        self.pdbEnter.clear()
        self.proteinButton.setEnabled(True)
        self.ligandButton.setEnabled(False)
        self.modelingButton.setEnabled(False)
        self.loadModelButton.setEnabled(True)
        self.saveModelButton.setEnabled(False)
        self.runScreeningButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.signal.stateInitial.emit()

    def state_protein_loaded(self):
        self.pdbEnter.setEnabled(False)
        self.proteinButton.setEnabled(False)
        self.ligandButton.setEnabled(True)
        self.modelingButton.setEnabled(False)
        self.loadModelButton.setEnabled(False)
        self.saveModelButton.setEnabled(False)
        self.runScreeningButton.setEnabled(False)
        self.clearButton.setEnabled(True)
        self.signal.stateProteinLoaded.emit()

    def state_ligand_loaded(self):
        self.pdbEnter.setEnabled(False)
        self.proteinButton.setEnabled(False)
        self.ligandButton.setEnabled(True)
        self.modelingButton.setEnabled(True)
        self.loadModelButton.setEnabled(False)
        self.saveModelButton.setEnabled(False)
        self.runScreeningButton.setEnabled(False)
        self.clearButton.setEnabled(True)
        self.signal.stateLigandLoaded.emit()

    def state_model_loaded(self):
        self.pdbEnter.setEnabled(False)
        self.proteinButton.setEnabled(False)
        self.ligandButton.setEnabled(False)
        self.modelingButton.setEnabled(False)
        self.loadModelButton.setEnabled(False)
        self.saveModelButton.setEnabled(True)
        self.runScreeningButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.signal.stateModelLoaded.emit()

    def state_all_stop(self):
        self.pdbEnter.setEnabled(False)
        self.proteinButton.setEnabled(False)
        self.ligandButton.setEnabled(False)
        self.modelingButton.setEnabled(False)
        self.loadModelButton.setEnabled(False)
        self.saveModelButton.setEnabled(False)
        self.runScreeningButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.signal.stateAllStop.emit()
