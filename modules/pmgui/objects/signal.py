from PyQt5.QtCore import pyqtSignal, QObject


class Signal(QObject):
    stateInitial = pyqtSignal()
    stateProteinLoaded = pyqtSignal()
    stateLigandLoaded = pyqtSignal()
    stateModelLoaded = pyqtSignal()
    stateAllStop = pyqtSignal()
