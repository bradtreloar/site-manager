
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


def backup_cms_app(app, site_info, aws_config):
    temp_dir = "/tmp/wordpress_backups/{}/".format(site_info["site_host"])
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


def backup_wordpress_site(args):
    site_info, aws_config = args
    backup_cms_app("wordpress", site_info, aws_config)


def backup_drupal_site(args):
    site_info, aws_config = args
    backup_cms_app("drupal", site_info, aws_config)
