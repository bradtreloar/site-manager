import os
import tarfile


def make_backup_archive(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tarball:
        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)
            tarball.add(filepath, arcname=filename)
