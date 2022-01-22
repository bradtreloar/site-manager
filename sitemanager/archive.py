import os
import tarfile


def make_backup_archive(filepath, source_dir):
    """
    Makes a gzipped tarball from the files in the given directory.

    Params:
        filepath: The path for the new tarball.
        source_dir: The directory containing the files to be archived.
    """
    # Make sure destination directory exists.
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Add each file to the tarball.
    with tarfile.open(filepath, "w:gz") as tarball:
        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)
            tarball.add(filepath, arcname=filename)
