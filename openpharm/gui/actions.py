import os
import tempfile
from pathlib import Path
import json

import pymol
from PyQt5 import QtWidgets

from .parse import download_pdb, parse_pdb
from .objects.pmnet_dialog import PMProgressDialog
from .screening_window import ScreeningDialog


def exportPyMOL(self):
    with tempfile.NamedTemporaryFile(suffix='.pse') as fd:
        pymol.cmd.save(fd.name)
        os.system(f'pymol {fd.name}')


def savePyMOLSession(self):
    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
        self,
        "Save PyMOL Session",
        "",
        "PyMOL Session Files (*.pse)",
        options=options
    )
    if fileName:
        pymol.cmd.save(fileName)
        self.print_log(f'Save PyMOL Session to {fileName}')


def saveModel(self):
    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
        self,
        "Save Pharmacophore Model File",
        self.binding_site,
        "Pharmacophore Model Files (*.pm)",
        options=options
    )
    if fileName:
        self.pharmacophore_model.save(fileName)
        self.print_log(f'Save Pharmacophore Model to {fileName}')


def openModel(self):
    options = QtWidgets.QFileDialog.Options()
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
        self,
        "Open Pharmacophore Model File",
        "",
        "Pharmacophore Model Files (*.pm)",
        options=options
    )
    if fileName:
        setup_model(self, fileName)


def loadRCSB(self):
    pdb_code = self.pdbEnter.text()
    if len(pdb_code) != 4:
        return
    pdb_download_dir = Path(f'./pdb/{pdb_code}')
    pdb_download_dir.mkdir(exist_ok=True, parents=True)
    protein_path = pdb_download_dir / f'{pdb_code}.pdb'
    if not protein_path.exists():
        self.print_log(f'Download {pdb_code} from https://www.rcsb.org...')
        flag = download_pdb(pdb_code, protein_path)
    else:
        self.print_log(f'Load {pdb_code} from {protein_path.absolute()}')
        flag = True

    if flag:
        setup_protein(self, protein_path)
        self.pdbEnter.setEnabled(False)
        self.proteinButton.setEnabled(False)

        ligand_path_dict = parse_pdb(pdb_code, protein_path, pdb_download_dir)
        for ligand_key in sorted(ligand_path_dict.keys()):
            setup_ligand(self, ligand_key, ligand_path_dict[ligand_key], load_pymol=False)
        pymol.cmd.zoom()
        self.treeWidget.setActiveLigand(list(ligand_path_dict.keys())[-1])
        self.print_log(f'Success to load {pdb_code}! ({len(self.ligand_path_dict)} ligands are detected)')
        if len(self.ligand_path_dict) > 0:
            self.state_ligand_loaded()
        else:
            self.state_protein_loaded()
    else:
        self.print_log(f'Fail to load {pdb_code}')


def openProtein(self):
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Protein File", "", "PDB Files (*.pdb)")
    if filename:
        self.print_log(f'Load {filename}')
        setup_protein(self, filename, remove_ligand=True)
        self.state_protein_loaded()


def openLigand(self):
    assert self.protein_path is not None
    filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Ligand File", "", "Mol Files (*.mol *.mol2 *.sdf)")
    if filename:
        ligand_key = Path(filename).stem
        setup_ligand(self, ligand_key, filename, load_pymol=True, is_active=True)
        self.state_ligand_loaded()


def clearSession(self):
    reply = QtWidgets.QMessageBox.question(
        self,
        'Clear Confirmation',
        'Do you want to clear session?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        QtWidgets.QMessageBox.No
    )
    if reply == QtWidgets.QMessageBox.No:
        return
    pymol.cmd.reinitialize('everything')
    self.treeWidget.clear()
    self.state_initial()
    self.print_log(f'Clear!')


def modeling(self):
    from openpharm.pmnet import PharmacophoreModel
    assert self.protein_path is not None

    ligand_path = self.treeWidget.active_ligand.filename
    binding_site_name = self.treeWidget.active_ligand.name
    pymol.cmd.disable(binding_site_name)
    pymol.cmd.zoom(self.treeWidget.active_ligand.surrounding_name)

    self.state_all_stop()
    self.print_log(f'Run Protein-based Pharmacophore Modeling...')

    def get_pharmacophore_model(text):
        if text is not None:
            self.pharmacophore_model = PharmacophoreModel()
            self.pharmacophore_model.__setstate__(json.loads(text))
        else:
            return None

    progress_dialog = PMProgressDialog(self, self.module, self.protein_path, ligand_path)
    progress_dialog.return_connect(get_pharmacophore_model)
    progress_dialog.exec_()

    if self.pharmacophore_model is not None:
        self.print_log(f'Total {len(self.pharmacophore_model.nodes)} hot spots are detected')
        for item in self.treeWidget.ligand_dict.values():
            self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
            self.treeWidget.ligand_dict = {}
            pymol.cmd.delete(item.name)
            pymol.cmd.delete(item.surrounding_name)
        self.binding_site = binding_site_name
        self.treeWidget.addModel(self.pharmacophore_model, self.binding_site)
        pymol.cmd.zoom('Surrounding')
        self.state_model_loaded()
    else:
        self.print_log(f'Stop Pharmacophore Modeling')
        pymol.cmd.enable(binding_site_name)
        self.state_ligand_loaded()


def openScreening(self):
    screening_dialog = ScreeningDialog(self)
    screening_dialog.exec_()


def setup_protein(self, filename, remove_ligand=False):
    pymol.cmd.load(str(filename))
    self.protein = Path(filename).stem
    self.protein_path = filename
    if remove_ligand:
        pymol.cmd.remove('hetatm')
        # self.print_log('Remove All Hetero Atoms (Ligand, Water, Metal)')
    else:
        pymol.cmd.remove('resn HOH,metal')
        # self.print_log('Remove Water and Metal')
    self.treeWidget.addProtein(self.protein)


def setup_ligand(self, key, filename, load_pymol=True, is_active=False):
    if load_pymol:
        org_key = key
        t = 0
        while key in self.ligand_path_dict:
            t += 1
            key = org_key + f'_{t}'
        pymol.cmd.load(str(filename), key)
        self.print_log(f'Load {filename}')
    else:
        pymol.cmd.color('atom', f'{key}')
    self.ligand_path_dict[key] = str(filename)

    self.treeWidget.addLigand(key, filename)
    if is_active:
        self.treeWidget.setActiveLigand(key)


def setup_model(self, filename):
    from openpharm.pmnet import PharmacophoreModel
    self.pharmacophore_model = PharmacophoreModel.load(filename)
    self.print_log(f'Load Pharmacophore Model ({filename})')
    with tempfile.TemporaryDirectory() as direc:
        protein_path = f'{direc}/{Path(filename).stem}.pdb'
        with open(protein_path, 'w') as w:
            w.write(self.pharmacophore_model.pdbblock)
        setup_protein(self, protein_path, remove_ligand=True)
    self.treeWidget.addModel(self.pharmacophore_model, self.protein)
    pymol.cmd.zoom('NCI*')
    self.state_model_loaded()
