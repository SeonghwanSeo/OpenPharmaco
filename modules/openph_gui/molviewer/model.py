import pymol
from openph_gui import setting as SETTING

from . import common
from .constant import (
    CHAIN_KEY,
    POCKET_KEY,
    PROTEIN_KEY,
    PHARMACOPHORE_POINT_KEY,
    HOTSPOT_KEY,
    NCI_KEY,
    INTERACTION_KEY,
    RESIDUE_KEY,
)


def create_nci(node) -> tuple[str, str, str, str, str]:
    key = f"{NCI_KEY}{node.index}"
    hotspot_color = SETTING.HOTSPOT_COLOR_DICT[node.interaction_type]
    interaction_color = SETTING.INTERACTION_COLOR_DICT[node.interaction_type]
    pharmacophore_color = SETTING.PHARMACOPHORE_POINT_COLOR_DICT[node.type]

    pharmacophore_key = f"{PHARMACOPHORE_POINT_KEY}{node.index}"
    pymol.cmd.pseudoatom(pharmacophore_key, pos=node.center, color=hotspot_color)
    pymol.cmd.color(pharmacophore_color, pharmacophore_key)
    pymol.cmd.set("sphere_scale", node.radius, pharmacophore_key)

    hotspot_key = f"{HOTSPOT_KEY}{node.index}"
    pymol.cmd.pseudoatom(hotspot_key, pos=node.hotspot_position, color=hotspot_color)
    pymol.cmd.color(hotspot_color, hotspot_key)

    interaction_key = f"{INTERACTION_KEY}{node.index}"
    pymol.cmd.distance(interaction_key, hotspot_key, pharmacophore_key)
    pymol.cmd.set("dash_color", interaction_color, interaction_key)

    residue_key = f"{RESIDUE_KEY}{node.index}"
    pymol.cmd.copy_to(residue_key, f"byres ({hotspot_key} around 2) and {PROTEIN_KEY}")
    pymol.cmd.color(SETTING.RESIDUE_HIGHLIGHT_COLOR, f"{residue_key} and elem C")

    common.group(key, [hotspot_key, residue_key, pharmacophore_key, interaction_key])
    return key, hotspot_key, residue_key, pharmacophore_key, interaction_key


def setup_model():
    pymol.cmd.color(SETTING.PROTEIN_COLOR, f"{PROTEIN_KEY} and elem C")
    pymol.cmd.enable(f"{CHAIN_KEY}*")
    pymol.cmd.set("sphere_scale", 0.2, f"{HOTSPOT_KEY}*")
    pymol.cmd.set("sphere_transparency", 0.2, f"{PHARMACOPHORE_POINT_KEY}*")
    pymol.cmd.set("dash_gap", 0.2, f"{INTERACTION_KEY}*")
    pymol.cmd.set("dash_length", 0.4, f"{INTERACTION_KEY}*")

    pymol.cmd.hide("label", f"{INTERACTION_KEY}*")
    pymol.cmd.hide("cartoon", f"{RESIDUE_KEY}*")
    pymol.cmd.hide("dot", f"{HOTSPOT_KEY}*")

    pymol.cmd.show("sphere", f"{HOTSPOT_KEY}*")
    pymol.cmd.show("sphere", f"{PHARMACOPHORE_POINT_KEY}*")
    pymol.cmd.show("line", f"{RESIDUE_KEY}*")
    pymol.cmd.show("dash", f"{INTERACTION_KEY}*")
    pymol.cmd.set("line_width", 2)
    pymol.cmd.zoom(f"{POCKET_KEY}")
