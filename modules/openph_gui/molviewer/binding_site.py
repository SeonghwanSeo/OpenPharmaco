import pymol
from openph_gui import setting as SETTING
from . import common
from .constant import CHAIN_KEY


def load(key, filename):
    ligand_key = f"{key}_ligand"
    surrounding_key = f"{key}_surrounding"
    pymol.cmd.load(str(filename), ligand_key)
    pymol.cmd.color(SETTING.LIGAND_COLOR, f"{ligand_key} and elem C")
    pymol.cmd.select(surrounding_key, f"byres ({key} around 10) and {CHAIN_KEY}*")
    pymol.cmd.deselect()
    common.group(key, [ligand_key, surrounding_key])


def enable(key):
    surrounding_key = f"{key}_surrounding"
    pymol.cmd.enable(key)
    pymol.cmd.color(SETTING.PROTEIN_COLOR, f"{CHAIN_KEY}* and elem C")
    pymol.cmd.color(SETTING.PROTEIN_HIGHLIGHT_COLOR, f"{surrounding_key} and elem C")
