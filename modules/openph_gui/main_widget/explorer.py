from pathlib import Path

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QBrush, QColor
import pymol


from openph_gui import setting as SETTING


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

    def clear(self):
        super().clear()
        self.ligand_dict = {}
        self.active_ligand = None

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clearSelection()

    def addProtein(self, name, filename):
        ProteinItem(self, name, name, filename)
        self.expandAll()

    def addBindingSite(self, name, key, filename):
        item = BindingSiteItem(self, name, key, filename)
        item.disable()
        self.ligand_dict[key] = item
        return item

    def setActiveLigand(self, key):
        self.ligand_dict[key].enable()

    def addModel(self, model, binding_site: str):
        pymol.cmd.color(SETTING.PROTEIN_COLOR, "Chain_* and elem C")
        for nci_type in SETTING.INTERACTION_TYPE_KEYS:
            key = "".join("".join(nci_type.split(" ")).split("-"))
            item = NCIGroupItem(self, nci_type, key, model)
            if item.childCount() == 0:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        pymol.cmd.select(
            "Surrounding", "byres (point* around 10) and Chain_* and elem C"
        )
        pymol.cmd.deselect()
        ChainHighlightItem(self, binding_site, "Surrounding")
        ElementVisualizeItem(self, "Residues", "residue*")
        ElementVisualizeItem(self, "Hotspots", "hotspot*")
        ElementVisualizeItem(self, "Interactions", "interaction*")
        ElementVisualizeItem(self, "Points", "point*")

        pymol.cmd.enable("Chain_*")
        pymol.cmd.set("sphere_scale", 0.2, "hotspot*")
        pymol.cmd.set("sphere_transparency", 0.2, f"point*")
        pymol.cmd.set("dash_gap", 0.2, "interaction*")
        pymol.cmd.set("dash_length", 0.4, "interaction*")

        pymol.cmd.hide("label", "interaction*")
        pymol.cmd.hide("cartoon", "residue*")
        pymol.cmd.hide("dot", "hotspot*")

        pymol.cmd.show("sphere", "hotspot*")
        pymol.cmd.show("sphere", "point*")
        pymol.cmd.show("line", "residue*")
        pymol.cmd.show("dash", "interaction*")
        pymol.cmd.set("line_width", 2)
        pymol.cmd.zoom("Surrounding NCI*")


class ToggleItem(QtWidgets.QTreeWidgetItem):
    TYPE = None
    ACTIVE_FOREGROUND = QBrush(QColor("#dddddd"))
    ACTIVE_BACKGROUND = QBrush(QColor("#606062"))

    INACTIVE_FOREGROUND = QBrush(QColor("#747475"))
    INACTIVE_BACKGROUND = QBrush(QColor("#1e1e1e"))

    def __init__(self, parent, group, name, *args, **kwargs):
        super().__init__(parent, (group, name), **kwargs)
        self.group = group
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

    def disable(self):
        self._state = False
        font = QFont()
        self.setFont(0, font)
        self.setForeground(0, self.INACTIVE_FOREGROUND)
        self.setBackground(0, self.INACTIVE_BACKGROUND)


class BindingSiteItem(ToggleItem):
    TYPE = "Ligand"

    def __init__(self, parent, name, key, filename, *args, **kwargs):
        super().__init__(parent, "BindingSite", name, *args, **kwargs)
        self.key = key
        self.ligand_key = f"{key}_ligand"
        self.surrounding_key = f"{key}_surrounding"
        pymol.cmd.load(str(filename), self.ligand_key)
        pymol.cmd.color(SETTING.LIGAND_COLOR, f"{self.ligand_key} and elem C")
        pymol.cmd.select(self.surrounding_key, f"byres ({key} around 10) and Chain*")
        pymol.cmd.deselect()
        pymol.cmd.group(self.key, f"{self.ligand_key} {self.surrounding_key}")
        self.ligand_item = LigandElementItem(self, key)
        self.ligand_item.enable()

    def enable(self):
        super().enable()
        parent = self._parent
        prev_active_ligand = parent.active_ligand
        if prev_active_ligand is self:
            return
        else:
            parent.active_ligand = self
            if prev_active_ligand is not None:
                prev_active_ligand.disable()
            pymol.cmd.enable(self.key)
            pymol.cmd.color(SETTING.PROTEIN_COLOR, "Chain* and elem C")
            pymol.cmd.color(
                SETTING.PROTEIN_HIGHLIGHT_COLOR, f"{self.surrounding_key} and elem C"
            )

    def disable(self):
        parent = self._parent
        if parent.active_ligand is self:
            return
        super().disable()
        pymol.cmd.disable(self.key)


class LigandElementItem(ToggleItem):
    TYPE = "Ligand"

    def __init__(self, parent, key, *args, **kwargs):
        super().__init__(parent, "Ligand", "ligand", *args, **kwargs)
        self.key = key

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.enable(self.key)


class ProteinItem(ToggleItem):
    def __init__(self, parent, name, key, filename, *args, **kwargs):
        super().__init__(parent, "Protein", name, *args, **kwargs)
        self.key = key
        pymol.cmd.load(str(filename), key)
        pymol.cmd.color(SETTING.PROTEIN_COLOR, f"{key} and elem C")
        pymol.cmd.remove("hetatm")
        pymol.cmd.remove("resn HOH,metal")
        for chain in pymol.cmd.get_chains(key):
            chain_key = f"Chain_{chain}"
            pymol.cmd.extract(chain_key, f"Chain {chain}")
            item = ProteinChainItem(self, chain, chain_key)
            item.enable()
        pymol.cmd.delete(key)
        pymol.cmd.group(key, "Chain*")

        stick = ProteinElementItem(self, "sticks", "sticks")
        line = ProteinElementItem(self, "lines", "lines")
        cartoon = ProteinElementItem(self, "cartoon", "cartoon")
        mesh = ProteinElementItem(self, "mesh", "mesh")
        surface = ProteinElementItem(self, "surface", "surface")
        stick.disable()
        line.disable()
        cartoon.enable()
        mesh.disable()
        surface.disable()

        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)


class ProteinElementItem(ToggleItem):
    TYPE = "ProteinElement"

    def __init__(self, parent, name, key, *args, **kwargs):
        super().__init__(parent, "Element", name, *args, **kwargs)
        self.key = key

    def enable(self):
        super().enable()
        pymol.cmd.show(self.key, "Chain*")

    def disable(self):
        super().disable()
        pymol.cmd.hide(self.key, "Chain*")


class ProteinChainItem(ToggleItem):
    TYPE = "ProteinChain"

    def __init__(self, parent, name, key, *args, **kwargs):
        super().__init__(parent, "Chain", name, *args, **kwargs)
        self.key = key

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)


class NCIGroupItem(ToggleItem):
    TYPE = "NCIGroup"

    def __init__(self, parent, name, key, model, *args, **kwargs):
        super().__init__(parent, "NCI", name, *args, **kwargs)
        self.key = key
        self.model = model
        self.item_list = []
        self.setForeground(1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[name])))
        for node in model.nodes:
            if SETTING.INTERACTION_TYPE_DICT[node.interaction_type] == name:
                self.item_list.append(ModelNodeItem(self, node))
        if len(self.item_list) > 0:
            pymol.cmd.group(self.key, " ".join(item.key for item in self.item_list))
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)


class ModelNodeItem(ToggleItem):
    TYPE = "Feature"

    def __init__(self, parent, node, *args, **kwargs):
        self.key = f"NCI{node.index}"
        name = SETTING.INTERACTION_NAME_DICT[node.interaction_type]
        super().__init__(parent, "Feature", name, *args, **kwargs)
        self.setForeground(
            1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[parent.name]))
        )

        hotspot_color = SETTING.INTERACTION_COLOR_DICT[node.interaction_type]
        pharmacophore_color = SETTING.PHARMACOPHORE_COLOR_DICT[node.type]

        hotspot_id = f"hotspot{node.index}"
        pymol.cmd.pseudoatom(hotspot_id, pos=node.hotspot_position, color=hotspot_color)
        pymol.cmd.color(hotspot_color, hotspot_id)
        ModelNodeElementItem(self, "hotspot", hotspot_id)

        residue_id = f"residue{node.index}"
        pymol.cmd.copy_to(residue_id, f"byres ({hotspot_id} around 2) and Chain*")
        pymol.cmd.color(SETTING.RESIDUE_HIGHLIGHT_COLOR, f"{residue_id} and elem C")
        ModelNodeElementItem(self, "residue", residue_id)

        pharmacophore_id = f"point{node.index}"
        pymol.cmd.pseudoatom(pharmacophore_id, pos=node.center, color=hotspot_color)
        pymol.cmd.color(pharmacophore_color, pharmacophore_id)
        pymol.cmd.set("sphere_scale", node.radius, pharmacophore_id)
        ModelNodeElementItem(self, "point", pharmacophore_id)

        interaction_id = f"interaction{node.index}"
        pymol.cmd.distance(interaction_id, hotspot_id, pharmacophore_id)
        pymol.cmd.set("dash_color", pharmacophore_color, interaction_id)
        ModelNodeElementItem(self, "interaction", interaction_id)

        pymol.cmd.group(
            self.key,
            f"{hotspot_id} {residue_id} {pharmacophore_id} {interaction_id}",
        )
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)


class ModelNodeElementItem(ToggleItem):
    TYPE = "FeatureElement"

    def __init__(self, parent, name, key, *args, **kwargs):
        super().__init__(parent, "Element", name, *args, **kwargs)
        self.key = key
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)


class ChainHighlightItem(ToggleItem):
    TYPE = "Visualize"

    def __init__(self, parent, name, key, *args, **kwargs):
        super().__init__(parent, "Binding Site", name, *args, **kwargs)
        self.key = key
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.color(SETTING.PROTEIN_HIGHLIGHT_COLOR, self.key)

    def disable(self):
        super().disable()
        pymol.cmd.color(SETTING.PROTEIN_COLOR, self.key)
        pymol.cmd.deselect()


class ElementVisualizeItem(ToggleItem):
    TYPE = "Visualize"

    def __init__(self, parent, name, key, *args, **kwargs):
        super().__init__(parent, "Visualize", name, *args, **kwargs)
        self.key = key
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.key)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.key)
