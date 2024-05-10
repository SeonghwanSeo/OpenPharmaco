from openbabel import pybel
from urllib.request import urlopen
from pathlib import Path

import pymol
from os import PathLike
from typing import Dict


def download_pdb(pdb_code: str, output_file: PathLike[str]):
    url = f'https://files.rcsb.org/download/{pdb_code.lower()}.pdb'
    try:
        with urlopen(url) as response:
            content = response.read().decode('utf-8')
            with open(output_file, 'w') as file:
                file.write(content)
        return True
    except Exception as e:
        print(f"Error downloading PDB file: {e}")
        return False


def parse_pdb(pdb_code: str, protein_path: PathLike[str], save_pdb_dir: PathLike[str]) -> Dict[str, str]:
    protein: pybel.Molecule = next(pybel.readfile('pdb', str(protein_path)))
    if 'HET' not in protein.data.keys():
        return {}
    het_lines = protein.data['HET'].split('\n')
    last_chain = protein.data['SEQRES'].split('\n')[-1].split()[1]
    del protein

    ligand_path_dict = {}
    for idx, line in enumerate(het_lines):
        vs = line.strip().split()
        if len(vs) == 4:
            ligid, authchain, residue_idx, _ = vs
        else:
            ligid, authchain, residue_idx, = vs[0], vs[1][0], vs[1][1:]
        if last_chain.startswith('Z'):
            pdbchain = f'Z_{idx}'
        else:
            pdbchain = chr(ord(last_chain) + 1)
        last_chain = pdbchain
        ligand_key = f"{pdb_code}_{pdbchain}_{ligid}"
        pymol.cmd.extract(ligand_key, f"resn {ligid} and resi {residue_idx} and chain {authchain}")
        ligand_path = str(Path(save_pdb_dir) / f'{ligand_key}.sdf')
        pymol.cmd.save(ligand_path, ligand_key)
        ligand_path_dict[ligand_key] = ligand_path
    return ligand_path_dict
