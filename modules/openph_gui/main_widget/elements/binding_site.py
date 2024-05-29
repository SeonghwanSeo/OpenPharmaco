from .base import ToggleItem
from openph_gui import molviewer


class BindingSiteItem(ToggleItem):
    GROUP = "Binding Site"

    def __init__(self, parent, name, key, filename, *args, **kwargs):
        super().__init__(parent, name, *args, **kwargs)
        self.key = key
        self.ligand_key = f"{key}_ligand"
        self.surrounding_key = f"{key}_surrounding"
        molviewer.binding_site.load(key, filename)
        self.ligand_item = LigandItem(self, key)
        self.ligand_item.enable()

    def _enable(self):
        parent = self._parent
        prev_active_ligand = parent.active_ligand
        if prev_active_ligand is self:
            return
        else:
            parent.active_ligand = self
            if prev_active_ligand is not None:
                prev_active_ligand.disable()
            molviewer.binding_site.enable(self.key)

    def _disable(self):
        molviewer.common.disable(self.key)

    def disable(self):
        parent = self._parent
        if parent.active_ligand is self:
            return
        super().disable()


class LigandItem(ToggleItem):
    GROUP = "Ligand"

    def __init__(self, parent, key):
        super().__init__(parent, "ligand")
        self.key = key

    def _enable(self):
        molviewer.common.enable(self.key)

    def _disable(self):
        molviewer.common.disable(self.key)
