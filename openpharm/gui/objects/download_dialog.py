from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread


class DownloadWorker(QThread):
    def __init__(self, weight_path):
        super().__init__()
        self.weight_path = weight_path

    def run(self):
        import gdown
        gdown.download('https://drive.google.com/uc?id=1gzjdM7bD3jPm23LBcDXtkSk18nETL04p', self.weight_path, quiet=False)


class DownloadDialog(QtWidgets.QDialog):
    def __init__(self, parent, weight_path):
        super().__init__(parent)

        self.setWindowTitle('Download PharmacoNet')
        self.setGeometry(600, 200, 200, 100)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        layout = QtWidgets.QVBoxLayout()
        self.statusLabel = QtWidgets.QLabel("Download PharmacoNet...", self)
        layout.addWidget(self.statusLabel)
        self.setLayout(layout)
        self.center_on_parent()

        self.worker = worker = DownloadWorker(str(weight_path))
        worker.finished.connect(self.close)
        worker.start()

    def center_on_parent(self):
        parent_center = self.parent().window.geometry().center()
        rect = self.geometry()
        rect.moveCenter(parent_center)
        self.move(rect.topLeft())

    def exec_(self):
        self.worker.start()
        super().exec_()
