
from datetime import datetime
import os
from unittest import TestCase
import unittest
from unittest.mock import MagicMock, patch

from sitemanager.backup import (
    TEMP_ARCHIVE_DIR_TEMPLATE,
    TEMP_BACKUPS_DIR_TEMPLATE,
    backup_app)
from tests.fakes import (
    fake_aws_config,
    fake_site,
    fake_site_ssh,
    random_string)


class BackupTests(TestCase):

    @patch("shutil.rmtree")
    @patch("shutil.copy")
    @patch("os.makedirs")
    @patch("sitemanager.backup.datetime", wraps=datetime)
    @patch("sitemanager.backup.make_gzipped_tarball")
    @patch("sitemanager.backup.get_remote_client")
    def test_backup_app_to_local(
            self,
            mock_get_remote_client,
            mock_make_gzipped_tarball,
            mock_datetime,
            mock_os_makedirs,
            mock_shutil_copy,
            mock_shutil_rmtree):
        """
        Stores a backup of an app on a local filesystem.
        """
        fake_datetime = datetime(2020, 1, 1)
        mock_datetime.now.return_value = fake_datetime
        fake_dirpath = random_string(20)
        site = fake_site()
        site.app = "wordpress"
        site.ssh_config = fake_site_ssh(site)
        backups_dirpath = TEMP_BACKUPS_DIR_TEMPLATE.format(site.host)
        archive_dirpath = TEMP_ARCHIVE_DIR_TEMPLATE.format(site.host)
        archive_filename = (
            f"{site.app}_backup_"
            f"{fake_datetime.isoformat(timespec='seconds')}"
            f".tar.gz")
        archive_filepath = f"{archive_dirpath}/{archive_filename}"
        mock_remote_client_instance = MagicMock()
        mock_remote_client = MagicMock()
        mock_remote_client.return_value = mock_remote_client_instance
        mock_get_remote_client.return_value = mock_remote_client

        backup_app(site, {
            "filesystem": "local",
            "path": fake_dirpath,
        })

        mock_get_remote_client.assert_called_with(site.app)
        mock_remote_client.assert_called_with(site.ssh_config.to_dict())
        mock_remote_client_instance.export_databases.assert_called_with(
            backups_dirpath)
        mock_remote_client_instance.download_generated_files.assert_called_with(
            backups_dirpath)
        mock_make_gzipped_tarball.assert_called_with(
            archive_filepath, backups_dirpath)
        mock_os_makedirs.assert_called_with(fake_dirpath, exist_ok=True)
        mock_shutil_copy.assert_called_with(archive_filepath, os.path.join(
            fake_dirpath, archive_filename))
        self.assertEqual(mock_shutil_rmtree.call_count, 2)

    @patch("os.makedirs")
    @patch("shutil.rmtree")
    @patch("sitemanager.backup.S3Client")
    @patch("sitemanager.backup.datetime", wraps=datetime)
    @patch("sitemanager.backup.make_gzipped_tarball")
    @patch("sitemanager.backup.get_remote_client")
    def test_backup_app_to_s3(
            self,
            mock_get_remote_client,
            mock_make_gzipped_tarball,
            mock_datetime,
            mock_s3_backup_client_class,
            mock_shutil_rmtree,
            mock_os_makedirs):
        """
        Stores a backup of an app on an S3 bucket.
        """
        frozen_datetime = datetime(2020, 1, 1)
        mock_datetime.now.return_value = frozen_datetime
        bucket_name = random_string(20)
        aws_config = fake_aws_config()
        site = fake_site()
        site.app = "wordpress"
        site.ssh_config = fake_site_ssh(site)
        backups_dirpath = TEMP_BACKUPS_DIR_TEMPLATE.format(site.host)
        archive_dirpath = TEMP_ARCHIVE_DIR_TEMPLATE.format(site.host)
        archive_filename = (
            f"{site.app}_backup_"
            f"{frozen_datetime.isoformat(timespec='seconds')}"
            f".tar.gz")
        archive_filepath = f"{archive_dirpath}/{archive_filename}"
        mock_remote_client = MagicMock()
        mock_remote_client_class = MagicMock()
        mock_remote_client_class.return_value = mock_remote_client
        mock_get_remote_client.return_value = mock_remote_client_class
        mock_s3_backup_client = MagicMock()
        mock_s3_backup_client_class.return_value = mock_s3_backup_client

        backup_app(site, {
            "filesystem": "s3",
            "bucket": bucket_name,
        }, aws_config)

        mock_get_remote_client.assert_called_with(site.app)
        mock_remote_client_class.assert_called_with(site.ssh_config.to_dict())
        mock_remote_client.export_databases.assert_called_with(
            backups_dirpath)
        mock_remote_client.download_generated_files.assert_called_with(
            backups_dirpath)
        mock_make_gzipped_tarball.assert_called_with(
            archive_filepath, backups_dirpath)
        mock_os_makedirs.assert_not_called()
        mock_s3_backup_client_class.assert_called_with(
            aws_config, bucket_name)
        mock_s3_backup_client.create_bucket.assert_called()
        mock_s3_backup_client.upload_archive_to_bucket.assert_called_with(
            archive_filepath)
        self.assertEqual(mock_shutil_rmtree.call_count, 2)


if __name__ == "__main__":
    unittest.main()
