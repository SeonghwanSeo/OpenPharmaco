from pathlib import Path
import multiprocessing
import time
from functools import partial

from PyQt5 import QtWidgets, QtCore

from typing import List, Optional, Dict, Tuple

from .utils import SettingDialog, ParameterSpinBox, FileQTableWidgetItem, ScoreQTableWidgetItem, EmptyQTableWidgetItem

from pmgui.setting import DARKMODE_STYLESHEET


# NOTE: Parameters
DEFAULT_WEIGHTS: Dict[str, float] = {
    'Cation': 8,
    'Anion': 8,
    'Aromatic': 4,
    'H-Bond Donor': 4,
    'H-Bond Acceptor': 4,
    'Halogen Atom': 4,
    'Hydrophobic': 1,
}

# NOTE: Parameters
DEFAULT_SETTING = {
    'Library Key': 'Name'
}


def worker(stop_event, work_queue, result_queue, pharmacophore_model, parameter):
    while not work_queue.empty() and not stop_event.is_set():
        item = work_queue.get()
        try:
            score = pharmacophore_model.scoring_file(item, parameter)
        except Exception:
            score = -1
        result_queue.put((item, score))


class ScreeningDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet(DARKMODE_STYLESHEET)
        self.setAcceptDrops(True)
        self.setWindowTitle('Screening')
        self.setGeometry(300, 300, 720, 360)
        self.pharmacophore_model: PharmacophoreModel = parent.pharmacophore_model
        self.setting = DEFAULT_SETTING.copy()
        self.parameter = DEFAULT_WEIGHTS.copy()

        self.library: List[Path] = []
        self.library_path: Optional[Path] = None
        self.result: List[Tuple[Path, float]] = []
        self.run_finished: bool = False
        self.saved: bool = False
        self.init_UI()
        self.state_initial()

    def init_UI(self):
        MAX_CPU = multiprocessing.cpu_count()
        main_layout = QtWidgets.QVBoxLayout()
        setting_layout = QtWidgets.QGridLayout()
        central_layout = QtWidgets.QHBoxLayout()

        main_layout.addLayout(setting_layout)
        main_layout.addLayout(central_layout)

        parameter_layout = QtWidgets.QVBoxLayout()
        result_layout = QtWidgets.QVBoxLayout()
        central_layout.addLayout(parameter_layout)
        central_layout.addLayout(result_layout)

        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 3)

        self.libraryButton = QtWidgets.QPushButton('Library', self)
        self.libraryButton.setMaximumHeight(25)
        self.libraryButton.clicked.connect(self.action_library)
        setting_layout.addWidget(self.libraryButton, 0, 0, 1, 1)
        self.libraryButton.setAutoDefault(False)
        self.libraryButton.setDefault(False)
        self.libraryLabel = QtWidgets.QPlainTextEdit("Directory not selected", self)
        self.libraryLabel.setReadOnly(True)
        self.libraryLabel.setMaximumHeight(25)
        setting_layout.addWidget(self.libraryLabel, 0, 1, 1, 7)

        self.cpuLabel = QtWidgets.QLabel('CPUs')
        self.cpuLabel.setAlignment(QtCore.Qt.AlignCenter)
        setting_layout.addWidget(self.cpuLabel, 1, 0, 1, 1)
        self.cpuSlider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.cpuSlider.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.cpuSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.cpuSlider.setValue(1)
        self.cpuSlider.setSingleStep(1)
        self.cpuSlider.setMinimum(1)
        self.cpuSlider.setMaximum(MAX_CPU)
        self.cpuSlider.valueChanged[int].connect(lambda v: self.cpuSpinBox.setValue(v))
        setting_layout.addWidget(self.cpuSlider, 1, 1, 1, 2)
        self.cpuSpinBox = QtWidgets.QSpinBox(self)
        self.cpuSpinBox.setMaximumHeight(25)
        self.cpuSpinBox.setMinimum(1)
        self.cpuSpinBox.setMaximum(MAX_CPU)
        self.cpuSpinBox.setValue(1)
        self.cpuSpinBox.valueChanged[int].connect(lambda v: self.cpuSlider.setValue(v))
        setting_layout.addWidget(self.cpuSpinBox, 1, 3, 1, 1)

        self.runButton = QtWidgets.QPushButton('Run!', self)
        self.runButton.clicked.connect(self.action_run)
        self.runButton.setMaximumHeight(25)
        self.runButton.setAutoDefault(False)
        self.runButton.setDefault(False)
        setting_layout.addWidget(self.runButton, 1, 4, 1, 1)
        self.saveButton = QtWidgets.QPushButton('Save', self)
        self.saveButton.clicked.connect(self.action_save)
        self.saveButton.setMaximumHeight(25)
        self.saveButton.setAutoDefault(False)
        self.saveButton.setDefault(False)
        setting_layout.addWidget(self.saveButton, 1, 5, 1, 1)
        self.clearButton = QtWidgets.QPushButton('Clear', self)
        self.clearButton.clicked.connect(self.action_clear)
        self.clearButton.setMaximumHeight(25)
        self.clearButton.setAutoDefault(False)
        self.clearButton.setDefault(False)
        setting_layout.addWidget(self.clearButton, 1, 6, 1, 1)
        self.advancedButton = QtWidgets.QPushButton('Advanced', self)
        self.advancedButton.clicked.connect(self.action_advanced)
        self.advancedButton.setMaximumHeight(25)
        self.advancedButton.setAutoDefault(False)
        self.advancedButton.setDefault(False)
        setting_layout.addWidget(self.advancedButton, 1, 7, 1, 1)

        parameter_grid_layout = QtWidgets.QGridLayout()
        parameterLabel = QtWidgets.QLabel('Parameter Setting')
        parameterLabel.setMinimumWidth(200)
        parameterLabel.setAlignment(QtCore.Qt.AlignCenter)
        parameter_grid_layout.addWidget(parameterLabel, 0, 0, 1, 2)
        self.parameter_widget_dict = {}
        for i, key in enumerate(['Cation', 'Anion', 'H-Bond Donor', 'H-Bond Acceptor',
                                 'Halogen Atom', 'Aromatic', 'Hydrophobic']):
            label = QtWidgets.QLabel(key)
            spinbox = ParameterSpinBox(self, key, self.parameter)
            spinbox.setMaximumHeight(20)
            spinbox.editingFinished.connect(self.focusNextChild)
            self.parameter_widget_dict[key] = spinbox
            parameter_grid_layout.addWidget(label, i + 1, 0, 1, 1)
            parameter_grid_layout.addWidget(spinbox, i + 1, 1, 1, 1)
        self.resetParameterButton = QtWidgets.QPushButton('Reset All')
        self.resetParameterButton.clicked.connect(self.action_reset_parameter)
        self.resetParameterButton.setAutoDefault(False)
        self.resetParameterButton.setDefault(False)
        parameter_grid_layout.addWidget(self.resetParameterButton, 8, 0, 1, 2)
        parameter_grid_layout.rowStretch(1)
        parameter_layout.addLayout(parameter_grid_layout)
        parameter_layout.setStretch(0, 0)
        parameter_layout.addStretch()

        self.tableLabel = QtWidgets.QLabel('Library not loaded')
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(['Key', 'Score'])
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(1, 100)
        result_layout.addWidget(self.tableLabel)
        result_layout.addWidget(self.tableWidget)

        self.setLayout(main_layout)
        self.center_on_parent()

    @property
    def cpu(self) -> int:
        return self.cpuSlider.value()

    def action_library(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.setup_library(directory)

    def setup_library(self, directory):
        self.libraryLabel.setPlainText(directory)
        self.library_path = Path(directory)
        self.library = list(self.library_path.rglob('*.sdf')) + list(self.library_path.rglob('*.mol2'))
        self.state_library_load()

        self.tableWidget.setRowCount(len(self.library))
        for i, file in enumerate(self.library):
            item = FileQTableWidgetItem(file, self.library_path, self.setting['Library Key'] == 'Path')
            self.tableWidget.setItem(i, 0, item)
            self.tableWidget.setItem(i, 1, EmptyQTableWidgetItem())
        self.tableLabel.setText(f'Library Size: {len(self.library)} Molecules')
        self.result = [None] * len(self.library)
        self.state_library_load()

    def action_run(self):
        work_queue = multiprocessing.Queue()
        result_queue = multiprocessing.Queue()

        num_items = len(self.library)
        for path in self.library:
            work_queue.put(path)

        weight = {
            'Cation': self.parameter['Cation'],
            'Anion': self.parameter['Anion'],
            'Aromatic': self.parameter['Aromatic'],
            'HBond_donor': self.parameter['H-Bond Donor'],
            'HBond_acceptor': self.parameter['H-Bond Acceptor'],
            'Halogen': self.parameter['Halogen Atom'],
            'Hydrophobic': self.parameter['Hydrophobic'],
        }
        self.state_all_stop()

        stop_event = multiprocessing.Event()
        _worker = partial(worker, pharmacophore_model=self.pharmacophore_model, parameter=weight)
        processes = [multiprocessing.Process(target=_worker, args=(stop_event, work_queue, result_queue)) for _ in range(self.cpu)]
        for p in processes:
            p.start()
        progress_dialog = QtWidgets.QProgressDialog("Screening...", "Abort", 0, num_items, self)
        progress_dialog.setCancelButton(None)
        progress_dialog.setAutoClose(True)
        progress_dialog.show()

        completed = 0
        while not result_queue.empty() or any(p.is_alive() for p in processes):
            QtWidgets.QApplication.processEvents()
            if progress_dialog.wasCanceled():
                stop_event.set()
                break
            while not result_queue.empty():
                key, score = result_queue.get()
                self.result[completed] = (key, score)
                completed += 1
                progress_dialog.setValue(completed)
            time.sleep(0.1)

        for p in processes:
            p.join()

        if progress_dialog.wasCanceled():
            self.state_library_load()
        else:
            self.result.sort(key=(lambda item: item[1]), reverse=True)
            for index, (file, score) in enumerate(self.result):
                item = FileQTableWidgetItem(file, self.library_path, self.setting['Library Key'] == 'Path')
                self.tableWidget.setItem(index, 0, item)
                self.tableWidget.setItem(index, 1, ScoreQTableWidgetItem(score))
            self.state_run_finished()

    def action_clear(self):
        if not self.saved:
            reply = QtWidgets.QMessageBox.question(
                self,
                'Clear Confirmation',
                'Do you want to save the result before clearing the session?',
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel
            )
            if reply == QtWidgets.QMessageBox.Cancel:
                return
            if reply == QtWidgets.QMessageBox.Save:
                self.action_save()
        for i, _ in enumerate(self.library):
            self.tableWidget.setItem(i, 1, EmptyQTableWidgetItem())
        self.result = [None] * len(self.result)
        self.state_library_load()

    def action_save(self):
        options = QtWidgets.QFileDialog.Options()
        assert self.library_path is not None
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Result Save File",
            Path(self.library_path).stem,
            "Result Files (*.csv *.txt)",
            options=options
        )
        if fileName:
            self.saved = True
            with open(fileName, 'w') as w:
                w.write('Key,PharmacoNetScore\n')
                for file, score in self.result:
                    if self.setting['Library Key'] == 'Name':
                        w.write(f'{file.stem},{score:.4f}\n')
                    else:
                        w.write(f'{file.relative_to(self.library_path)},{score:.4f}\n')

    def action_advanced(self):
        initial_setting = self.setting.copy()
        dialog = SettingDialog(self, self.setting)
        dialog.exec_()
        # NOTE: Library Key
        if self.library_path is not None:
            if initial_setting['Library Key'] != self.setting['Library Key']:
                for index in range(len(self.library)):
                    item = self.tableWidget.item(index, 0)
                    if self.setting['Library Key'] == 'Name':
                        item.to_filename()
                    else:
                        item.to_filepath()

    def action_set_parameter(self, value, key):
        self.parameter[key] = value

    def action_reset_parameter(self):
        self.parameter = DEFAULT_WEIGHTS
        for key, spinbox in self.parameter_widget_dict.items():
            spinbox.setValue(DEFAULT_WEIGHTS[key])

    def center_on_parent(self):
        rect = self.geometry()
        rect.moveCenter(self.parent().window.geometry().center())
        self.move(rect.topLeft())

    def closeEvent(self, event):
        if self.run_finished and not self.saved:
            reply = QtWidgets.QMessageBox.question(
                self,
                'Clear Confirmation',
                'Do you want to save the result before close?',
                QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Cancel,
                QtWidgets.QMessageBox.Cancel
            )
            if reply == QtWidgets.QMessageBox.Cancel:
                event.ignore()
                return
            if reply == QtWidgets.QMessageBox.Save:
                self.action_save()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.ignore()  # Ignore the ESC key press
        else:
            super().keyPressEvent(event)  # Handle other key events normally

    def state_initial(self):
        self.libraryButton.setEnabled(True)
        self.runButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.run_finished: bool = False
        self.resetParameterButton.setEnabled(True)
        self.saved = False

    def state_library_load(self):
        self.libraryButton.setEnabled(True)
        self.runButton.setEnabled(True)
        self.saveButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.run_finished: bool = False
        for spinbox in self.parameter_widget_dict.values():
            spinbox.setEnabled(True)
        self.resetParameterButton.setEnabled(True)
        self.saved = False

    def state_all_stop(self):
        self.libraryButton.setEnabled(False)
        self.runButton.setEnabled(False)
        self.saveButton.setEnabled(False)
        self.clearButton.setEnabled(False)
        self.run_finished: bool = False
        for spinbox in self.parameter_widget_dict.values():
            spinbox.setEnabled(False)
        self.resetParameterButton.setEnabled(False)
        self.saved = False

    def state_run_finished(self):
        self.libraryButton.setEnabled(False)
        self.runButton.setEnabled(False)
        self.saveButton.setEnabled(True)
        self.clearButton.setEnabled(True)
        self.run_finished: bool = True
        for spinbox in self.parameter_widget_dict.values():
            spinbox.setEnabled(False)
        self.resetParameterButton.setEnabled(False)
        self.saved = False

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.libraryButton.isEnabled():
            if event.mimeData().hasUrls:
                for url in event.mimeData().urls():
                    if url.isLocalFile():
                        url = url.toLocalFile()
                    else:
                        url = url.toString()
                    self.setup_library(url)
                event.accept()
