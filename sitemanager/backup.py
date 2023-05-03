
from datetime import datetime, timezone
import os
import shutil

from sitemanager.archive import make_gzipped_tarball
from sitemanager.aws import S3Client
from sitemanager.config import AWSConfig, BackupConfig
from sitemanager.models import Site
from sitemanager.remote import get_remote_client
from sitemanager.remote.wordpress import WordpressClient
from sitemanager.remote.drupal import DrupalClient


TEMP_BACKUPS_DIR_TEMPLATE = "/tmp/backups/{}"
TEMP_ARCHIVE_DIR_TEMPLATE = "/tmp/archives/{}"


def backup_app(
        site: Site,
        backup_config: BackupConfig,
        aws_config: AWSConfig = None):
    """
    Downloads the files and database for a Wordpress site and uploads them to 
    an S3 bucket as an archive file.
    """
    print(site.host)

    # Temporary directory for storing backups.
    backups_dirpath = TEMP_BACKUPS_DIR_TEMPLATE.format(site.host)

    # Initialise app client.
    app_client = get_remote_client(site.app)(site.ssh_config.to_dict())

    print("- Exporting database.")
    app_client.export_databases(backups_dirpath)

    print("- Downloading site files.")
    app_client.download_generated_files(backups_dirpath)

    print("- Creating tarball.")
    archive_dirpath = TEMP_ARCHIVE_DIR_TEMPLATE.format(site.host)
    archive_filename = (
        f"{site.app}_backup_{datetime.now(timezone.utc).isoformat(timespec='seconds')}"
        f".tar.gz")
    archive_filepath = f"{archive_dirpath}/{archive_filename}"
    make_gzipped_tarball(archive_filepath, backups_dirpath)

    if is_s3_backup(backup_config):
        print("- Uploading to S3.")
        bucket_name = backup_config["bucket"].format(site_host=site.host)
        s3_backup_bucket_client = S3Client(aws_config, bucket_name)
        s3_backup_bucket_client.create_bucket()
        s3_backup_bucket_client.upload_archive_to_bucket(archive_filepath)
    else:
        print("- Copying to backup directory.")
        dirpath = backup_config["path"].format(site_host=site.host)
        os.makedirs(dirpath, exist_ok=True)
        shutil.copy(archive_filepath, os.path.join(dirpath, archive_filename))

    # Delete temporary files.
    shutil.rmtree(backups_dirpath)
    shutil.rmtree(archive_dirpath)


def is_s3_backup(backup_config: BackupConfig):
    return backup_config["filesystem"].lower() == "s3"
