from PyQt5 import QtWidgets


class SettingDialog(QtWidgets.QDialog):
    def __init__(self, parent, setting):
        super().__init__(parent)
        self.setting = setting
        self.initUI()
        self.center_on_parent()

    def initUI(self):
        self.setWindowTitle('Advanced Settings')
        self.setGeometry(100, 100, 300, 200)
        self.layout = layout = QtWidgets.QFormLayout()
        self.add_key_widget()
        self.setLayout(layout)

    def add_key_widget(self):
        key_widget = QtWidgets.QWidget(self)
        key_layout = QtWidgets.QHBoxLayout(self)
        label = QtWidgets.QLabel('Library Key:')
        radiobutton_name = QtWidgets.QRadioButton('File Name', key_widget)
        radiobutton_name.clicked.connect(lambda: self.setting.update({'Library Key': 'Name'}))
        radiobutton_path = QtWidgets.QRadioButton('File Path', key_widget)
        radiobutton_path.clicked.connect(lambda: self.setting.update({'Library Key': 'Path'}))
        if self.setting['Library Key'] == 'Name':
            radiobutton_name.setChecked(True)
        else:
            radiobutton_path.setChecked(True)
        key_layout.addWidget(label)
        key_layout.addWidget(radiobutton_name)
        key_layout.addWidget(radiobutton_path)
        key_widget.setLayout(key_layout)
        self.layout.addRow(key_widget)

    def center_on_parent(self):
        rect = self.geometry()
        rect.moveCenter(self.parent().window().geometry().center())
        self.move(rect.topLeft())


class ParameterSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self, parent, key, parameter):
        super().__init__(parent)
        self.key = key
        self.parameter = parameter
        self.default_value = float(parameter[key])
        self.setValue(float(parameter[key]))
        self.setSingleStep(1)
        self.setDecimals(1)
        self.valueChanged.connect(self.update_value)

    def update_value(self, value):
        self.parameter[self.key] = value
        default_value = self.default_value
        if value < default_value:
            self.setStyleSheet("color: coral;")
        elif value > default_value:
            self.setStyleSheet("color: lightblue;")
        else:
            self.setStyleSheet("color: #e7e7e7;")
