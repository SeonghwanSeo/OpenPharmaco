import os
import tempfile
from pathlib import Path
import json

from urllib.request import urlopen
from PyQt5 import QtWidgets, QtCore, QtGui

from openph_gui.dialogs.pmnet_dialog import PMProgressDialog
from openph_gui.screening_widget import ScreeningDialog
from openph_gui import molviewer


def openWiki(self):
    url = QtCore.QUrl("https://github.com/SeonghwanSeo/OpenPharmaco/wiki")
    QtGui.QDesktopServices.openUrl(url)


def openPaper(self):
    url = QtCore.QUrl("https://arxiv.org/abs/2310.00681")
    QtGui.QDesktopServices.openUrl(url)


def exportPyMOL(self):
    import pymol

    with tempfile.NamedTemporaryFile(suffix=".pse", delete=False) as fd:
        pass
    pymol.cmd.save(fd.name)
    os.system(f"pymol {fd.name}")
    os.remove(fd.name)


def savePyMOLSession(self):
    import pymol

    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
        self, "Save PyMOL Session", "", "PyMOL Session Files (*.pse)", options=options
    )
    if fileName:
        pymol.cmd.save(fileName)
        self.print_log(f"Save PyMOL Session to {fileName}")


def saveModel(self):
    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
        self,
        "Save Pharmacophore Model File",
        self.binding_site,
        "Pharmacophore Model Files (*.pm)",
        options=options,
    )
    if fileName:
        self.pharmacophore_model.save(fileName)
        self.print_log(f"Save Pharmacophore Model to {fileName}")


def openModel(self):
    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Open Pharmacophore Model File",
        "",
        "Pharmacophore Model Files (*.pm)",
        options=options,
    )
    if fileName:
        setup_model(self, fileName)


def loadRCSB(self):
    pdb_code = self.pdbEnter.text()
    if len(pdb_code) != 4:
        return
    pdb_download_dir = Path(f"./pdb/{pdb_code}")
    pdb_download_dir.mkdir(exist_ok=True, parents=True)
    protein_path = pdb_download_dir / f"{pdb_code}.pdb"
    if not protein_path.exists():
        self.print_log(f"Download {pdb_code} from https://www.rcsb.org...")
        flag = download_pdb(pdb_code, protein_path)
    else:
        self.print_log(f"Load {pdb_code} from {protein_path.absolute()}")
        flag = True

    if flag:
        parse_pdb(self, pdb_code, protein_path, pdb_download_dir)
        self.print_log(
            f"Success to load {pdb_code}! ({len(self.ligand_path_dict)} ligands are detected)"
        )
    else:
        self.print_log(f"Fail to load {pdb_code}")


def openProtein(self):
    protein_path, _ = QtWidgets.QFileDialog.getOpenFileName(
        self, "Open Protein File", "", "PDB Files (*.pdb)"
    )
    if protein_path:
        self.print_log(f"Load {protein_path}")
        prefix = Path(protein_path).stem.replace(" ", "_")
        Path("./pdb/").mkdir(exist_ok=True)
        pdb_download_dir = tempfile.TemporaryDirectory(prefix=f"{prefix}_", dir="./pdb")
        parse_pdb(self, prefix, protein_path, pdb_download_dir.name)


def openLigand(self):
    assert self.protein_path is not None
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(
        self, "Open Ligand File", "", "Mol Files (*.mol *.mol2 *.sdf *.pdb)"
    )
    if filename:
        ligand_key = Path(filename).stem.replace(" ", "_")
        print(ligand_key)
        setup_ligand(self, ligand_key, filename, is_active=True)
        self.state_ligand_loaded()


def clearSession(self):
    reply = QtWidgets.QMessageBox.question(
        self,
        "Clear Confirmation",
        "Do you want to clear session?",
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No,
    )
    if reply == QtWidgets.QMessageBox.No:
        return
    molviewer.common.clear()
    self.treeWidget.clear()
    self.state_initial()
    self.print_log("Clear!")


def modeling(self):
    from pmnet import PharmacophoreModel

    assert self.protein_path is not None

    self.state_all_stop()
    self.print_log("Run Protein-based Pharmacophore Modeling...")

    active_ligand = self.treeWidget.active_ligand
    ligand_path = self.ligand_path_dict[active_ligand.key]
    molviewer.common.disable(active_ligand.key)
    molviewer.common.zoom(active_ligand.surrounding_key)

    progress_dialog = PMProgressDialog(
        self, self.module, self.protein_path, ligand_path
    )

    def get_pharmacophore_model(jsonblock):
        if jsonblock is not None:
            self.pharmacophore_model = PharmacophoreModel()
            self.pharmacophore_model.__setstate__(json.loads(jsonblock))
        else:
            return None

    progress_dialog.return_connect(get_pharmacophore_model)
    progress_dialog.exec_()

    if self.pharmacophore_model is not None:
        self.print_log(
            f"Total {len(self.pharmacophore_model.nodes)} hot spots are detected"
        )
        for item in self.treeWidget.ligand_dict.values():
            self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
            self.treeWidget.ligand_dict = {}
            molviewer.common.delete(item.name)
            molviewer.common.delete(item.surrounding_key)
        self.binding_site = active_ligand.name
        self.treeWidget.addModel(self.pharmacophore_model, self.binding_site)
        self.state_model_loaded()
    else:
        self.print_log("Stop Pharmacophore Modeling")
        molviewer.common.enable(active_ligand.name)
        self.state_ligand_loaded()


def openScreening(self):
    screening_dialog = ScreeningDialog(self)
    screening_dialog.exec_()


# NOTE: FUNCTIONS
def setup_protein(self, filename):
    self.protein = Path(filename).stem.replace(" ", "_")
    self.protein_path = filename
    self.treeWidget.addProtein(self.protein, self.protein_path)
    molviewer.common.bg_color("white")


def setup_ligand(self, name, filename, is_active=False):
    t = 0
    while f"{name}_{t}" in self.ligand_path_dict:
        t += 1
    key = f"{name}_{t}"
    self.treeWidget.addBindingSite(name, key, filename)
    self.ligand_path_dict[key] = str(filename)
    self.print_log(f"Load {filename}")
    if is_active:
        self.treeWidget.setActiveLigand(key)


def setup_model(self, filename):
    from pmnet import PharmacophoreModel

    self.pharmacophore_model = PharmacophoreModel.load(filename)
    self.print_log(f"Load Pharmacophore Model ({filename})")
    with tempfile.TemporaryDirectory() as direc:
        protein_path = f"{direc}/{Path(filename).stem}.pdb"
        with open(protein_path, "w") as w:
            w.write(self.pharmacophore_model.pdbblock)
        setup_protein(self, protein_path)
    self.treeWidget.addModel(self.pharmacophore_model, self.protein)
    self.state_model_loaded()


# NOTE: PDB
def download_pdb(pdb_code: str, output_file):
    url = f"https://files.rcsb.org/download/{pdb_code.lower()}.pdb"
    try:
        with urlopen(url) as response:
            content = response.read().decode("utf-8")
            with open(output_file, "w") as file:
                file.write(content)
        return True
    except Exception as e:
        print(f"Error downloading PDB file: {e}")
        return False


def parse_pdb(self, pdb_code: str, protein_path, save_pdb_dir):
    from Bio.PDB import PDBParser, PDBIO, Select

    class LigandSelect(Select):
        def __init__(self, ligand):
            self.ligand = ligand

        def accept_residue(self, residue):
            return residue == self.ligand

    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("structure", protein_path)
    io = PDBIO()

    ligand_path_list = []
    for model in structure:
        for chain in model:
            for residue in chain:
                hetflag, resseq, _ = residue.get_id()
                if hetflag not in (" ", "W"):
                    ligand_key = f"{pdb_code}_{chain.id}_{residue.get_resname()}"
                    ligand_selector = LigandSelect(residue)
                    ligand_path = os.path.join(
                        save_pdb_dir,
                        f"{ligand_key}_{resseq}.pdb",
                    )
                    io.set_structure(structure)
                    io.save(ligand_path, select=ligand_selector)
                    ligand_path_list.append((ligand_key, ligand_path))
    setup_protein(self, protein_path)
    for ligand_key, ligand_path in ligand_path_list:
        setup_ligand(self, ligand_key, ligand_path)
    molviewer.common.zoom()
    if len(self.ligand_path_dict) > 0:
        self.treeWidget.setActiveLigand(list(self.ligand_path_dict.keys())[-1])
        self.state_ligand_loaded()
    else:
        self.state_protein_loaded()
