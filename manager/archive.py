import os
import tarfile


def make_backup_archive(filepath, source_dir):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with tarfile.open(filepath, "w:gz") as tarball:
        for filename in os.listdir(source_dir):
            filepath = os.path.join(source_dir, filename)
            tarball.add(filepath, arcname=filename)
