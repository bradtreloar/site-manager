
from datetime import datetime
import os
import shutil
from manager.archive import make_backup_archive
from manager.remote.wordpress import WordpressClient
from manager.remote.drupal import DrupalClient
from manager.aws import S3BackupBucketClient


CLIENTS = {
    "drupal": DrupalClient,
    "wordpress": WordpressClient,
}


def backup_wordpress_site(args):
    site_info, aws_config = args
    app = "wordpress"
    temp_dir = "/tmp/{}_backups/{}/".format(app, site_info["site_host"])
    # Download backup.
    client = CLIENTS[app](
        site_info["ssh_config"], site_info["backup_bucket"])
    client.start_webauth_session()
    client.export_database(temp_dir + "/data/{}.sql".format(app))
    client.download_site_files(temp_dir)
    # Create backup tarball.
    archive_dirpath = "/tmp/archives/{}".format(site_info["site_host"])
    archive_filepath = "{}/{}_backup_{}.tar.gz".format(
        archive_dirpath,
        app,
        datetime.now().isoformat()
    )
    make_backup_archive(archive_filepath, temp_dir)
    # Upload tarball to S3.
    s3_backup_bucket_client = S3BackupBucketClient(
        aws_config, site_info["backup_bucket"])
    s3_backup_bucket_client.create()
    s3_backup_bucket_client.upload_archive(archive_filepath)
    # Cleanup temporary files.
    shutil.rmtree(temp_dir)
    shutil.rmtree(archive_dirpath)


def backup_drupal_site(args):
    site_info, aws_config = args
    app = "drupal"
    temp_dir = "/tmp/{}_backups/{}/".format(app, site_info["site_host"])
    client = CLIENTS[app](
        site_info["ssh_config"], site_info["backup_bucket"])
    client.start_webauth_session()
    # Get site names
    site_names = client.site_names()
    # Download backups.
    for site_name in site_names:
        client.export_database(site_name, temp_dir)
        client.download_site_files(site_name, temp_dir)
    # Create backup tarball.
    archive_dirpath = "/tmp/archives/{}".format(site_info["site_host"])
    archive_filepath = "{}/{}_backup_{}.tar.gz".format(
        archive_dirpath,
        app,
        datetime.now().isoformat()
    )
    make_backup_archive(archive_filepath, temp_dir)
    # Upload tarball to S3.
    s3_backup_bucket_client = S3BackupBucketClient(
        aws_config, site_info["backup_bucket"])
    s3_backup_bucket_client.create()
    s3_backup_bucket_client.upload_archive(archive_filepath)
    # Cleanup temporary files.
    shutil.rmtree(temp_dir)
    shutil.rmtree(archive_dirpath)
