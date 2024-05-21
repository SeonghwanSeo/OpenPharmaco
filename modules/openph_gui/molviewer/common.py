from collections.abc import Sequence
import pymol


def delete(arg: str):
    pymol.cmd.delete(arg)


def enable(arg: str):
    pymol.cmd.enable(arg)


def disable(arg: str):
    pymol.cmd.disable(arg)


def zoom(arg: str | None = None):
    if arg is not None:
        pymol.cmd.zoom(arg)
    else:
        pymol.cmd.zoom()


def clear():
    pymol.cmd.reinitialize("everything")


def bg_color(color: str):
    pymol.cmd.bg_color(color)


def group(group_name: str, element_names: Sequence[str]):
    pymol.cmd.group(group_name, " ".join(element_names))
