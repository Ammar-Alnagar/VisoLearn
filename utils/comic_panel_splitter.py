import os
import shutil
from pathlib import Path

from new_image_splitting import AutomatedCollageSplitter

__all__ = ["split_comic_panels"]


def split_comic_panels(image_path: str | os.PathLike, output_dir: str | os.PathLike | None = None, debug: bool = False):
    """Split a comic page image into individual panel images and save them.

    This is a thin wrapper around :pyclass:`new_image_splitting.AutomatedCollageSplitter` that
    conforms to the legacy signature expected by ``reference.comic_image_generator``.
    It ensures that the output filenames follow the ``panel_XX.png`` convention used
    elsewhere in the codebase.

    Parameters
    ----------
    image_path : str | Path
        Path to the source comic image (PNG/JPG/etc.).
    output_dir : str | Path | None, optional
        Destination directory where the individual panel images will be written.  If
        *None*, a sibling directory named ``<stem>_panels`` will be created next to
        the source image.
    debug : bool, optional
        When *True*, additional debug images will be produced by the underlying splitter.
    """

    image_path = Path(image_path)
    if output_dir is None:
        output_dir = image_path.parent / f"{image_path.stem}_panels"
    output_dir = Path(output_dir)

    splitter = AutomatedCollageSplitter()
    segments_info = splitter.split_collage(image_path, output_dir=output_dir, debug=debug)

    # Rename files from segment_XX.png to panel_XX.png to match existing expectations.
    for idx, info in enumerate(segments_info, start=1):
        original_path = Path(info["path"])
        # Only act if filename starts with "segment_"
        if original_path.name.startswith("segment_"):
            target_name = f"panel_{idx:02d}.png"
            target_path = original_path.parent / target_name
            try:
                shutil.move(str(original_path), str(target_path))
                info["path"] = str(target_path)
            except Exception as exc:
                # If renaming fails, keep original file and continue.
                print(f"⚠ Could not rename {original_path} -> {target_name}: {exc}")

    return segments_info 