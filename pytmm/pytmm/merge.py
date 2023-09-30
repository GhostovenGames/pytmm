# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from PIL import Image
from typing import Iterable
from itertools import accumulate
from os.path import abspath


def _determine_tile_size(images: Iterable[Image.Image]) -> tuple[int, int]:
    """Get the singular tile size.

    Calculate the smallest box that will fit all images within,
    effectivelly the tile size.

    Args:
        images (Iterable[Image.Image]): An iterable of image objects.

    Returns:
        tuple[int, int]: The smallest box that fits all of the image objects
        inside itself.
    """
    # Gives a tuple of ((Xs), (Ys)) for each image.
    sizes = []
    for image in images:
        sizes.append(image.size)
        image.close()
    xys = (*zip(*sizes),)
    return max(xys[0]), max(xys[1])


def _determine_final_size(
    tile_size: tuple[int, int], column_count: int, tile_count: int
) -> tuple[int, int]:
    """Determine the final size of the tileset.

    Given the singular tile size and tile count per row, determine
    what the final tileset will have as a size.

    Args:
        tile_size (tuple[int, int], column_count): Size of a single tile.
        column_count (int): Number of tiles per row.
        tile_count: (int): Number of total tiles.

    Returns:
        tuple[int, int]: Size of the whole tile sheet.
    """
    w_unit, h_unit = tile_size
    tileset_width = w_unit * min(tile_count, column_count)
    # For height we need to calculate the number of rows.
    row_count = max(1, tile_count // column_count)
    tileset_height = row_count * h_unit
    return tileset_width, tileset_height


def resize_and_centre(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Given an image create a copy of it that is padded to be this size.

    This effectivelly resizes the canvas of the image without scaling the
    image itself.

    Args:
        image (Image.Image): Source image.
        copy_canvas (Image.Image): Canvas to be copied into.

    Returns:
        Image.Image: Copied version of the image that is centered.
    """
    copy_canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    image_w, image_h = image.size
    canvas_w, canvas_h = size
    space_w = canvas_w - image_w
    space_h = canvas_h - image_h
    w_offset = space_w // 2
    h_offset = space_h // 2
    copy_canvas.paste(image.copy(), (w_offset, h_offset, image_w, image_h))
    return copy_canvas


def _generate_tileset_from_files(
    files: tuple[str, ...], column_count: int
) -> Image.Image:
    """Given a list of files generate a tileset from them.

    Generate a tileset from the given list of image files.

    Args:
        files (tuple[str]): List of paths to the image files.
        column_count (_type_): Number of columns per row.

    Returns:
        Image.Image: Tileset image
    """
    # We want to conserve memory to avoid having to load
    # vast amount of images but we need to make two passes
    # at least so we create iterator factory.
    images = lambda: (Image.open(abspath(file)) for file in files)
    # Size of the location to paste.
    tile_size = _determine_tile_size(images())
    tileset_size = _determine_final_size(tile_size, column_count, len(files))
    tileset = Image.new("RGBA", tileset_size, (0, 0, 0, 0))
    for i, image in enumerate(images()):
        resized_image = resize_and_centre(image, tile_size)
        dst_box = (
            # Current w-offset depends on the modulo since it repeats each row.
            (i % column_count) * tile_size[0],
            # h-offset depends on which row we are.
            (i // column_count) * tile_size[1],
        )  # ie where to paste.
        tileset.paste(resized_image, dst_box)
        image.close()
    return tileset


def merge_tiles(files: tuple[str, ...], outfile: str, column_count: int) -> None:
    """Merge a list of tile files to a single tileset.

    Args:
        files (tuple[str, ...]): List of file paths.
        outfile (str): Name of the out file.
        column_count (int): Number of tiles per row.
    """
    tileset = _generate_tileset_from_files(files, column_count)
    tileset.save(outfile)
