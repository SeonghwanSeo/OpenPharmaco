import pymol
from openph_gui import setting as SETTING

from . import common
from .constant import PROTEIN_KEY, POCKET_KEY, PHARMACOPHORE_POINT_KEY, CHAIN_KEY


def load(filename) -> list[tuple[str, str]]:
    chain_list = []
    tmp_protein_key = "_PROTEIN_TMP_"
    pymol.cmd.load(str(filename), tmp_protein_key)
    pymol.cmd.color(SETTING.PROTEIN_COLOR, f"{tmp_protein_key} and elem C")
    pymol.cmd.remove("hetatm")
    pymol.cmd.remove("resn HOH,metal")
    for chain in pymol.cmd.get_chains(tmp_protein_key):
        chain_key = f"{CHAIN_KEY}{chain}"
        pymol.cmd.extract(chain_key, f"Chain {chain}")
        chain_list.append((chain, chain_key))
    pymol.cmd.delete(tmp_protein_key)
    common.group(PROTEIN_KEY, [chain_key for _, chain_key in chain_list])
    return chain_list


def enable_element(key):
    pymol.cmd.show(key, PROTEIN_KEY)


def disable_element(key):
    pymol.cmd.hide(key, PROTEIN_KEY)


def enable():
    pymol.cmd.enable(PROTEIN_KEY)


def disable():
    pymol.cmd.disable(PROTEIN_KEY)


def get_pocket():
    pymol.cmd.select(
        POCKET_KEY,
        f"byres ({PHARMACOPHORE_POINT_KEY}* around 10) and {PROTEIN_KEY} and elem C",
    )
    pymol.cmd.deselect()


def enable_pocket():
    pymol.cmd.color(SETTING.PROTEIN_HIGHLIGHT_COLOR, f"{POCKET_KEY} and elem C")


def disabe_pocket():
    pymol.cmd.color(SETTING.PROTEIN_COLOR, f"{POCKET_KEY} and elem C")
