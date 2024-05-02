import json

from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal


class PMNetWorker(QThread):
    progress_updated = pyqtSignal(str, int)
    result = pyqtSignal(str)

    def __init__(self, pmnet, protein_path, ligand_path):
        super().__init__()
        self.force_stop = False
        self.pmnet = pmnet
        self.protein_path = protein_path
        self.ligand_path = ligand_path

    def run(self):
        model = self.pmnet.run_gui(self.protein_path, self.ligand_path, self)
        if model is not None:
            self.result.emit(json.dumps(model.__getstate__()))
        else:
            return None

    def stop(self):
        self.force_stop = True


class PMProgressDialog(QtWidgets.QDialog):
    def __init__(self, parent, module, protein_path, ligand_path):
        super().__init__(parent)
        self.setWindowTitle('PharmacoNet Running...')
        self.setGeometry(150, 25, 300, 50)
        layout = QtWidgets.QVBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Starting...", self)
        layout.addWidget(self.statusLabel)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximum(100)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        self.center_on_parent()

        self.worker = worker = PMNetWorker(module, protein_path, ligand_path)
        worker.progress_updated.connect(self.updateProgressDialog)
        worker.finished.connect(self.close)
        worker.start()

    def updateProgressDialog(self, message, value):
        self.progressBar.setValue(value)
        self.statusLabel.setText(message)

    def center_on_parent(self):
        parent_geometry = self.parent().window.geometry()
        parent_center = parent_geometry.topLeft() + self.parent().ext_layout.geometry().center()
        rect = self.geometry()
        rect.moveCenter(parent_center)
        self.move(rect.topLeft())

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)

    def return_connect(self, function):
        self.worker.result.connect(function)

    def exec_(self):
        self.worker.start()
        super().exec_()
