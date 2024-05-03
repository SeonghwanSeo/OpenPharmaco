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
        gdown.download('https://drive.google.com/uc?id=1gzjdM7bD3jPm23LBcDXtkSk18nETL04p', self.weight_path, quiet=True)


class ProgressWorker(QThread):
    progress = pyqtSignal(int)

    def __init__(self, weight_dir):
        super().__init__()
        self.weight_dir = weight_dir

    def run(self):
        while True:
            size = list(os.popen(f'du -sh {self.weight_dir.parent}'))[0].split()[0]
            if not size.endswith('M'):
                size = 0
            else:
                size = float(size[:-1])
            self.progress.emit(min(int(size / 130 * 100), 100))
            if size > 130:
                break
            time.sleep(2)


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, parent, weight_path):
        super().__init__(parent)

        self.setWindowTitle('Google Drive Download')
        self.setGeometry(600, 200, 300, 100)
        self.setMinimumSize(200, 100)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        layout = QtWidgets.QVBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Download PharmacoNet...", self)
        layout.addWidget(self.statusLabel)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximum(100)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        self.center_on_parent()

        weight_dir = weight_path.parent
        os.system(f'/bin/rm -rf {weight_dir}')
        weight_dir.mkdir()
        self.worker = worker = DownloadWorker(str(weight_path))
        self.progressworker = progressworker = ProgressWorker(weight_dir)
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
