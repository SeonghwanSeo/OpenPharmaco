PROTEIN_COLOR = 'gray90'
PROTEIN_HIGHLIGHT_COLOR = 'red'
RESIDUE_HIGHLIGHT_COLOR = 'black'

PHARMACOPHORE_COLOR_DICT = {
    'Hydrophobic': 'orange',
    'Aromatic': 'deeppurple',
    'Cation': 'blue',
    'Anion': 'red',
    'HBond_acceptor': 'magenta',
    'HBond_donor': 'cyan',
    'Halogen': 'yellow',
}

INTERACTION_COLOR_DICT = {
    'Hydrophobic': 'orange',
    'PiStacking_P': 'deeppurple',
    'PiStacking_T': 'deeppurple',
    'PiCation_lring': 'blue',
    'PiCation_pring': 'deeppurple',
    'HBond_ldon': 'magenta',
    'HBond_pdon': 'cyan',
    'SaltBridge_lneg': 'blue',
    'SaltBridge_pneg': 'red',
    'XBond': 'yellow',
}

INTERACTION_TYPE_DICT = {
    'Hydrophobic': 'Hydrophobic',
    'PiStacking_P': 'Aromatic',
    'PiStacking_T': 'Aromatic',
    'PiCation_lring': 'Aromatic',
    'PiCation_pring': 'Cation',
    'HBond_ldon': 'H-Bond Donor',
    'HBond_pdon': 'H-Bond Acceptor',
    'SaltBridge_lneg': 'Anion',
    'SaltBridge_pneg': 'Cation',
    'XBond': 'Halogen Atom',
}

INTERACTION_NAME_DICT = {
    'Hydrophobic': 'Hydrophobic',
    'PiStacking_P': 'PiStacking (Parallel)',
    'PiStacking_T': 'PiStacking (T-shaped)',
    'PiCation_lring': 'Pi-Cation',
    'PiCation_pring': 'Pi-Cation',
    'HBond_ldon': 'H-Bond',
    'HBond_pdon': 'H-Bond',
    'SaltBridge_lneg': 'Salt Bridge',
    'SaltBridge_pneg': 'Salt Bridge',
    'XBond': 'Halogen Bond',
}
INTERACTION_TYPE_KEYS = [
    'Hydrophobic',
    'Aromatic',
    'Anion',
    'Cation',
    'H-Bond Donor',
    'H-Bond Acceptor',
    'Halogen Atom',
]

INTERACTION_COLOR_DICT_GUI = {
    'Hydrophobic': 'orange',
    'Aromatic': 'purple',
    'Anion': 'red',
    'Cation': 'blue',
    'H-Bond Donor': 'cyan',
    'H-Bond Acceptor': 'magenta',
    'Halogen Atom': 'yellow',
}

DARKMODE_STYLESHEET = """
    QMainWindow {
        background-color: #2c2c2e;
    }
    QPushButton {
        background-color: #606062;
        color: #e7e7e7;
        border: 1px solid #28282a;
        border-radius: 5px;
        padding: 2px;
    }
    QPushButton:pressed {
        background-color: #78787a;
    }
    QPushButton:hover {
        border: 2px solid #78787a;
    }
    QPushButton:focus {
        border: 2px solid #78787a;
    }
    QPushButton:disabled {
        background-color: #464647;
        color: #747475;
    }
    QLabel {
        color: #e7e7e7;
    }
    QSpinBox {
        color: #e7e7e7;
    }
    QDoubleSpinBox {
        color: #e7e7e7;
    }
    QPlainTextEdit {
        background-color: #1e1e1e;
        color: #e7e7e7;
    }
    QTreeWidget {
        background-color: #1e1e1e;
        color: #e7e7e7;
    }
    QHeaderView::section {
        background-color: #2c2c2e;
        color: #e7e7e7;
    }
    QLineEdit {
        background-color: #1e1e1e;
        color: #595959;
        border: 1px solid #494949;
        border-radius: 2px;
        padding: 1px 6px;
    }
    QLineEdit:focus {
        color: #e7e7e7;
        border: 1px solid #747475;
        border-radius: 2px;
        padding: 1px 6px;
    }
    QLineEdit:disabled {
        background-color: #464647;
        color: #747475;
        border-radius: 2px;
        padding: 1px 6px;
    }
    QLineEdit:disabled {
        background-color: #464647;
        color: #747475;
        border-radius: 2px;
        padding: 1px 6px;
    }
    """
