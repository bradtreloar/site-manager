import os
from os import PathLike
import tarfile


def make_gzipped_tarball(dest_filepath: PathLike, src_dir: PathLike):
    # Make sure destination directory exists.
    os.makedirs(os.path.dirname(dest_filepath), exist_ok=True)

    # Add each file to the tarball.
    with tarfile.open(dest_filepath, "w:gz") as tarball:
        for filename in os.listdir(src_dir):
            src_filepath = os.path.join(src_dir, filename)
            tarball.add(src_filepath, arcname=filename)
