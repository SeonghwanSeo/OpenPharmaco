from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QBrush, QColor


class ToggleItem(QtWidgets.QTreeWidgetItem):
    GROUP = "BASE"
    ACTIVE_FOREGROUND = QBrush(QColor("#dddddd"))
    ACTIVE_BACKGROUND = QBrush(QColor("#606062"))

    INACTIVE_FOREGROUND = QBrush(QColor("#747475"))
    INACTIVE_BACKGROUND = QBrush(QColor("#1e1e1e"))

    def __init__(self, parent, name: str):
        super().__init__(parent, (self.GROUP, name))
        self.name = name
        self._parent = parent
        self._state = True

    def toggle(self):
        if self._state:
            self.disable()
        else:
            self.enable()

    def enable(self):
        self._state = True
        font = QFont()
        self.setFont(0, font)
        self.setForeground(0, self.ACTIVE_FOREGROUND)
        self.setBackground(0, self.ACTIVE_BACKGROUND)
        self._enable()

    def disable(self):
        self._state = False
        font = QFont()
        self.setFont(0, font)
        self.setForeground(0, self.INACTIVE_FOREGROUND)
        self.setBackground(0, self.INACTIVE_BACKGROUND)
        self._disable()

    def _enable(self):
        pass

    def _disable(self):
        pass
