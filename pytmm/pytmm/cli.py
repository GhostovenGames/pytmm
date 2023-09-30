# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import click
from PIL import ImageFile
from .merge import merge_tiles


@click.group()
def pytmm():
    """Python Tilemap Manager to manage your tile maps!"""
    pass


@click.command()
@click.option(
    "-o",
    "--out",
    default="tilemap.png",
    show_default=True,
    help="Name of the tilemap output file.",
)
@click.option(
    "-c", "--columns", default=4, show_default=True, help="Number of columns per row."
)
@click.option(
    "-f/-nf",
    "--force-truncated/--disable-force-truncated",
    default=False,
    help="If provided, forces the underlying library to load the files even if they have CRC errors.",
)
@click.argument("files", nargs=-1, required=True)
def merge(out: str, columns: int, files: tuple[str, ...], force_truncated: bool):
    """Merge multiple image files given by [FILES] to a tilemap"""
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = force_truncated
        merge_tiles(files, out, columns)
    except FileNotFoundError as e:
        raise click.FileError(e.filename, hint="File not found.")


pytmm.add_command(merge)
