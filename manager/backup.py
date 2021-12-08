
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


def backup_wordpress_site(
        site_id,
        site_host,
        ssh_config,
        backup_bucket,
        aws_config):
    app = "wordpress"
    temp_dir = "/tmp/{}_backups/{}/".format(app, site_host)
    # Download backup.
    client = CLIENTS[app](
        ssh_config, backup_bucket)
    client.start_webauth_session()
    client.export_database(temp_dir + "/data/{}.sql".format(app))
    client.download_site_files(temp_dir)
    # Create backup tarball.
    archive_dirpath = "/tmp/archives/{}".format(site_host)
    archive_filepath = "{}/{}_backup_{}.tar.gz".format(
        archive_dirpath,
        app,
        datetime.now().isoformat()
    )
    make_backup_archive(archive_filepath, temp_dir)
    # Upload tarball to S3.
    s3_backup_bucket_client = S3BackupBucketClient(
        aws_config, backup_bucket)
    s3_backup_bucket_client.create()
    s3_backup_bucket_client.upload_archive(archive_filepath)
    # Cleanup temporary files.
    shutil.rmtree(temp_dir)
    shutil.rmtree(archive_dirpath)


def backup_drupal_site(
        site_id,
        site_host,
        ssh_config,
        backup_bucket,
        aws_config):
    app = "drupal"
    temp_dir = "/tmp/{}_backups/{}/".format(app, site_host)
    client = CLIENTS[app](ssh_config, backup_bucket)
    client.start_webauth_session()
    # The Drupal installation may include several sites, so we need to collect
    # the machine name and database settings for each.
    sites_settings = client.sites_settings()
    # Download backups
    for site_name, site_settings in sites_settings.items():
        client.export_database(site_name, site_settings, temp_dir)
        client.download_site_files(site_name, temp_dir)
    # Create backup tarball.
    archive_dirpath = "/tmp/archives/{}".format(site_host)
    archive_filepath = "{}/{}_backup_{}.tar.gz".format(
        archive_dirpath,
        app,
        datetime.now().isoformat()
    )
    make_backup_archive(archive_filepath, temp_dir)
    # Upload tarball to S3.
    s3_backup_bucket_client = S3BackupBucketClient(aws_config, backup_bucket)
    s3_backup_bucket_client.create()
    s3_backup_bucket_client.upload_archive(archive_filepath)
    # Clean up temporary files.
    shutil.rmtree(temp_dir)
    shutil.rmtree(archive_dirpath)
