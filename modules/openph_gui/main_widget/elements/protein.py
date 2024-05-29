from .base import ToggleItem
from openph_gui import molviewer


class ProteinItem(ToggleItem):
    GROUP = "Protein"

    def __init__(self, parent, name, filename):
        super().__init__(parent, name)
        print(filename)
        chain_list = molviewer.protein.load(filename)
        for chain, chain_key in chain_list:
            item = ChainItem(self, chain, chain_key)
            item.enable()

        ProteinElementItem(self, "Cartoon", "cartoon").enable()
        ProteinElementItem(self, "Stick", "sticks").disable()
        ProteinElementItem(self, "Line", "lines").disable()
        ProteinElementItem(self, "Mesh", "mesh").disable()
        ProteinElementItem(self, "Surface", "surface").disable()
        self.enable()

    def _enable(self):
        molviewer.protein.enable()

    def _disable(self):
        molviewer.protein.disable()


class ChainItem(ToggleItem):
    GROUP = "Chain"

    def __init__(self, parent, name, key):
        super().__init__(parent, name)
        self.key = key

    def _enable(self):
        molviewer.common.enable(self.key)

    def disable(self):
        super().disable()
        molviewer.common.disable(self.key)


class ProteinElementItem(ToggleItem):
    GROUP = "Element"

    def __init__(self, parent, name, key):
        super().__init__(parent, name)
        self.key = key

    def _enable(self):
        molviewer.protein.enable_element(self.key)

    def _disable(self):
        molviewer.protein.disable_element(self.key)


class PocketItem(ToggleItem):
    GROUP = "Binding Site"

    def __init__(self, parent, name):
        super().__init__(parent, name)
        molviewer.protein.get_pocket()
        self.enable()

    def _enable(self):
        molviewer.protein.enable_pocket()

    def _disable(self):
        molviewer.protein.disabe_pocket()
