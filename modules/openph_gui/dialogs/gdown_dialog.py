from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import time
import gdown
import os


class DownloadWorker(QThread):
    def __init__(self, weight_path):
        super().__init__()
        self.weight_path = weight_path

    def run(self):
        gdown.download(
            "https://drive.google.com/uc?id=1gzjdM7bD3jPm23LBcDXtkSk18nETL04p",
            self.weight_path,
            quiet=True,
        )


class ProgressWorker(QThread):
    progress = pyqtSignal(int)

    def __init__(self, weight_path):
        super().__init__()
        self.weight_dir = weight_path.parent

    def run(self):
        while True:
            size = 0
            for file in self.weight_dir.iterdir():
                size += os.path.getsize(file)
            size = int(size / (1024**2))
            self.progress.emit(min(int(size / 130 * 100), 100))
            if size > 130:
                break
            time.sleep(0.5)


class GDownDialog(QtWidgets.QDialog):
    def __init__(self, parent, weight_path):
        super().__init__(parent)

        self.setWindowTitle("PharmacoNet Installation")
        self.setGeometry(600, 200, 300, 100)
        self.setMinimumSize(200, 100)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        layout = QtWidgets.QVBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Download PharmacoNet (139 MB) ...", self)
        layout.addWidget(self.statusLabel)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximum(100)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        self.center_on_parent()

        weight_path.parent.mkdir(exist_ok=True)
        for file in weight_path.parent.iterdir():
            os.remove(file)
        self.worker = worker = DownloadWorker(str(weight_path))
        self.progressworker = progressworker = ProgressWorker(weight_path)
        worker.finished.connect(self.close)
        progressworker.progress.connect(self.progressBar.setValue)
        progressworker.start()
        worker.start()

    def center_on_parent(self):
        parent_center = self.parent().window.geometry().center()
        rect = self.geometry()
        rect.moveCenter(parent_center)
        self.move(rect.topLeft())

    def exec_(self):
        self.worker.start()
        self.progressworker.start()
        super().exec_()
