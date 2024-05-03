from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QBrush, QColor
import pymol

from typing import Dict, Optional

from openpharm import setting as SETTING


class ViewerQTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTreeWidget::item:selected {
                background-color: white;
                color: black;
            }
        """)
        self.ligand_dict: Dict[str, LigandItem] = {}
        self.active_ligand: Optional[LigandItem] = None
        self.setHeaderLabels(['Type', 'Name'])

    def clear(self):
        super().clear()
        self.ligand_dict = {}
        self.active_ligand = None

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.clearSelection()

    def addProtein(self, name):
        ProteinItem(self, name)

    def addLigand(self, name, filename):
        item = LigandItem(self, name, filename)
        item.disable()
        self.ligand_dict[name] = item
        return item

    def setActiveLigand(self, name):
        self.ligand_dict[name].enable()

    def addModel(self, model, binding_site: str):
        pymol.cmd.color(SETTING.PROTEIN_COLOR, 'Chain_* and elem C')
        for nci_type in SETTING.INTERACTION_TYPE_KEYS:
            item = NCITypeItem(self, nci_type, model)
            if item.childCount() == 0:
                self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        pymol.cmd.select('Surrounding', 'byres (point* around 10) and Chain_* and elem C')
        pymol.cmd.deselect()
        ChainHighlight(self, binding_site, 'Surrounding')
        ElementVisualize(self, 'Residues', 'residue*')
        ElementVisualize(self, 'Hotspots', 'hotspot*')
        ElementVisualize(self, 'Interactions', 'interaction*')
        ElementVisualize(self, 'Points', 'point*')

        pymol.cmd.enable('Chain_*')
        pymol.cmd.set('sphere_scale', 0.2, 'hotspot*')
        pymol.cmd.set('sphere_transparency', 0.2, f'point*')
        pymol.cmd.set('dash_gap', 0.2, 'interaction*')
        pymol.cmd.set('dash_length', 0.4, 'interaction*')

        pymol.cmd.hide('label', 'interaction*')
        pymol.cmd.hide('cartoon', 'residue*')
        pymol.cmd.hide('dot', 'hotspot*')

        pymol.cmd.show('sphere', 'hotspot*')
        pymol.cmd.show('sphere', 'point*')
        pymol.cmd.show('line', 'residue*')
        pymol.cmd.show('dash', 'interaction*')
        pymol.cmd.set('line_width', 2)


class ToggleItem(QtWidgets.QTreeWidgetItem):
    TYPE = None
    ACTIVE_FOREGROUND = QBrush(QColor('#dddddd'))
    ACTIVE_BACKGROUND = QBrush(QColor('#606062'))

    INACTIVE_FOREGROUND = QBrush(QColor('#747475'))
    INACTIVE_BACKGROUND = QBrush(QColor('#1e1e1e'))

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
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


class LigandItem(ToggleItem):
    TYPE = 'Ligand'

    def __init__(self, parent, name, filename, *args, **kwargs):
        super().__init__(parent, ('Ligand', name), *args, **kwargs)
        self.name = name
        self.pymol_name = name
        self.surrounding_name = f'{name}_surrounding'
        self.filename = filename
        pymol.cmd.select(self.surrounding_name, f'byres ({name} around 10) and Chain*')
        pymol.cmd.deselect()
        pymol.cmd.show('sticks', self.pymol_name)

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
            pymol.cmd.color(SETTING.PROTEIN_COLOR, f'Chain* and elem C')
            pymol.cmd.enable(self.pymol_name)
            pymol.cmd.color(SETTING.PROTEIN_HIGHLIGHT_COLOR, f'{self.surrounding_name} and elem C')

    def disable(self):
        parent = self._parent
        if parent.active_ligand is self:
            return
        super().disable()
        pymol.cmd.disable(self.pymol_name)
        pymol.cmd.color(SETTING.PROTEIN_COLOR, f'Chain* and elem C')


class ProteinElementQTreeWidget(ToggleItem):
    TYPE = 'ProteinElement'

    def __init__(self, parent, name, *args, **kwargs):
        super().__init__(parent, ('Element', name), *args, **kwargs)
        self.name = name
        self.pymol_name = name

    def enable(self):
        super().enable()
        pymol.cmd.show(self.pymol_name, f'Chain*')

    def disable(self):
        super().disable()
        pymol.cmd.hide(self.pymol_name, f'Chain*')


class ProteinChainQTreeWidget(ToggleItem):
    TYPE = 'ProteinChain'

    def __init__(self, parent, name, *args, **kwargs):
        self.name = f'{parent.name}_{name}'
        self.pymol_name = f'Chain_{self.name}'
        super().__init__(parent, ('Chain', self.name), *args, **kwargs)
        pymol.cmd.extract(self.pymol_name, f'Chain {name}')

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)


class ProteinItem(ToggleItem):
    def __init__(self, parent, name, *args, **kwargs):
        super().__init__(parent, ('Protein', name), *args, **kwargs)
        self.name = name
        self.pymol_name = name
        pymol.cmd.color(SETTING.PROTEIN_COLOR, f'{name} and elem C')
        for chain in pymol.cmd.get_chains(name):
            item = ProteinChainQTreeWidget(self, chain)
            item.enable()
        pymol.cmd.delete(name)
        pymol.cmd.group(name, 'Chain*')

        stick = ProteinElementQTreeWidget(self, 'sticks')
        line = ProteinElementQTreeWidget(self, 'lines')
        cartoon = ProteinElementQTreeWidget(self, 'cartoon')
        mesh = ProteinElementQTreeWidget(self, 'mesh')
        surface = ProteinElementQTreeWidget(self, 'surface')
        stick.disable()
        line.disable()
        cartoon.enable()
        mesh.disable()
        surface.disable()

        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)


class NCITypeItem(ToggleItem):
    TYPE = 'NCIType'

    def __init__(self, parent, name, model, *args, **kwargs):
        super().__init__(parent, ('NCI', name), *args, **kwargs)
        self.model = model
        self.name = name
        self.pymol_name = ''.join(''.join(name.split(' ')).split('-'))
        self.item_list = []
        self.setForeground(1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[name])))
        for node in model.nodes:
            if SETTING.INTERACTION_TYPE_DICT[node.interaction_type] == self.name:
                self.item_list.append(ModelNodeItem(self, node))
        if len(self.item_list) > 0:
            pymol.cmd.group(self.pymol_name, ' '.join(item.pymol_name for item in self.item_list))
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)


class ModelNodeItem(ToggleItem):
    TYPE = 'Feature'

    def __init__(self, parent, node, *args, **kwargs):
        self.name = SETTING.INTERACTION_NAME_DICT[node.interaction_type]
        self.pymol_name = f'NCI{node.index}'
        super().__init__(parent, ('Feature', self.name), *args, **kwargs)
        self.setForeground(1, QBrush(QColor(SETTING.INTERACTION_COLOR_DICT_GUI[parent.name])))

        hotspot_color = SETTING.INTERACTION_COLOR_DICT[node.interaction_type]
        pharmacophore_color = SETTING.PHARMACOPHORE_COLOR_DICT[node.type]

        hotspot_id = f'hotspot{node.index}'
        pymol.cmd.pseudoatom(hotspot_id, pos=node.hotspot_position, color=hotspot_color)
        pymol.cmd.color(hotspot_color, hotspot_id)
        ModelNodeElementItem(self, 'hotspot', hotspot_id)

        residue_id = f'residue{node.index}'
        pymol.cmd.copy_to(residue_id, f'byres ({hotspot_id} around 2) and Chain*')
        pymol.cmd.color(SETTING.RESIDUE_HIGHLIGHT_COLOR, f'{residue_id} and elem C')
        ModelNodeElementItem(self, 'residue', residue_id)

        pharmacophore_id = f'point{node.index}'
        pymol.cmd.pseudoatom(pharmacophore_id, pos=node.center, color=hotspot_color)
        pymol.cmd.color(pharmacophore_color, pharmacophore_id)
        pymol.cmd.set('sphere_scale', node.radius, pharmacophore_id)
        ModelNodeElementItem(self, 'point', pharmacophore_id)

        interaction_id = f'interaction{node.index}'
        pymol.cmd.distance(interaction_id, hotspot_id, pharmacophore_id)
        pymol.cmd.set('dash_color', pharmacophore_color, interaction_id)
        ModelNodeElementItem(self, 'interaction', interaction_id)

        pymol.cmd.group(self.pymol_name, f'{hotspot_id} {residue_id} {pharmacophore_id} {interaction_id}')
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)


class ModelNodeElementItem(ToggleItem):
    TYPE = 'FeatureElement'

    def __init__(self, parent, name, pymol_name, *args, **kwargs):
        super().__init__(parent, ('Element', name), *args, **kwargs)
        self.name = pymol_name
        self.pymol_name = pymol_name
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)


class ChainHighlight(ToggleItem):
    TYPE = 'Visualize'

    def __init__(self, parent, name, pymol_name, *args, **kwargs):
        super().__init__(parent, ('Binding Site', name), *args, **kwargs)
        self.name = pymol_name
        self.pymol_name = pymol_name
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.color(SETTING.PROTEIN_HIGHLIGHT_COLOR, self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.color(SETTING.PROTEIN_COLOR, self.pymol_name)
        pymol.cmd.deselect()


class ElementVisualize(ToggleItem):
    TYPE = 'Visualize'

    def __init__(self, parent, name, pymol_name, *args, **kwargs):
        super().__init__(parent, ('Visualize', name), *args, **kwargs)
        self.name = name
        self.pymol_name = pymol_name
        self._parent = parent
        self.enable()

    def enable(self):
        super().enable()
        pymol.cmd.enable(self.pymol_name)

    def disable(self):
        super().disable()
        pymol.cmd.disable(self.pymol_name)
