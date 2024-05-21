from PyQt5 import QtWidgets

from openph_gui import molviewer
from openph_gui import setting as SETTING
from .elements.protein import ProteinItem, PocketItem
from .elements.binding_site import BindingSiteItem
from .elements.model import NCIGroupItem, VisualizeItem


class OpenPHExplorer(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet(
            """
            Item::item:selected {
                background-color: white;
                color: black;
            }
        """
        )
        self.ligand_dict: dict[str, BindingSiteItem] = {}
        self.active_ligand: BindingSiteItem | None = None
        self.setHeaderLabels(["Type", "Name"])
        self.setColumnWidth(0, 120)

    def clear(self):
        super().clear()
        self.ligand_dict = {}
        self.active_ligand = None

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clearSelection()

    def addProtein(self, name, filename):
        ProteinItem(self, name, filename)
        self.expandAll()

    def addBindingSite(self, name, key, filename):
        item = BindingSiteItem(self, name, key, filename)
        item.disable()
        self.ligand_dict[key] = item
        return item

    def setActiveLigand(self, key):
        self.ligand_dict[key].enable()

    def addModel(self, model, binding_site: str):
        for nci_type in SETTING.INTERACTION_TYPE_KEYS:
            item = NCIGroupItem(self, nci_type, model)
            if item.childCount() == 0:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        pocket = PocketItem(self, binding_site)
        VisualizeItem(self, "Residues", "residue*")
        VisualizeItem(self, "Hotspots", "hotspot*")
        VisualizeItem(self, "Interactions", "interaction*")
        VisualizeItem(self, "Points", "point*")
        molviewer.model.setup_model()
        pocket.enable()
