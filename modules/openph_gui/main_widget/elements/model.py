from PyQt5.QtGui import QBrush, QColor

from openph_gui import molviewer
from openph_gui import setting as SETTING
from .base import ToggleItem


class NCIGroupItem(ToggleItem):
    GROUP = "NCI"

    def __init__(self, parent, name, model):
        super().__init__(parent, name)
        self.key = name.replace(" ", "").replace("-", "")
        self.model = model
        self.item_list = []
        self.setForeground(1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[name])))
        for node in model.nodes:
            if SETTING.INTERACTION_TYPE_DICT[node.interaction_type] == name:
                self.item_list.append(ModelNodeItem(self, node))
        molviewer.common.group(self.key, [item.key for item in self.item_list])
        self.enable()

    def _enable(self):
        molviewer.common.enable(self.key)

    def _disable(self):
        molviewer.common.disable(self.key)


class ModelNodeItem(ToggleItem):
    GROUP = "Feature"

    def __init__(self, parent, node):
        name = SETTING.INTERACTION_NAME_DICT[node.interaction_type]
        super().__init__(parent, name)
        self.setForeground(
            1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[parent.name]))
        )
        self.key, hotspot_key, residue_key, point_key, interaction_key = (
            molviewer.model.create_nci(node)
        )
        ModelNodeElementItem(self, "hotspot", hotspot_key)
        ModelNodeElementItem(self, "residue", residue_key)
        ModelNodeElementItem(self, "point", point_key)
        ModelNodeElementItem(self, "interaction", interaction_key)
        self.enable()

    def enable(self):
        super().enable()
        molviewer.common.enable(self.key)

    def disable(self):
        super().disable()
        molviewer.common.disable(self.key)


class ModelNodeElementItem(ToggleItem):
    GROUP = "Element"

    def __init__(self, parent, name, key):
        super().__init__(parent, name)
        self.key = key
        self._parent = parent
        self.enable()

    def _enable(self):
        molviewer.common.enable(self.key)

    def _disable(self):
        molviewer.common.disable(self.key)


class VisualizeItem(ToggleItem):
    GROUP = "Visualize"

    def __init__(self, parent, name, key):
        super().__init__(parent, name)
        self.key = key
        self.enable()

    def _enable(self):
        molviewer.common.enable(self.key)

    def _disable(self):
        molviewer.common.disable(self.key)
