import random
from unittest import TestCase
import unittest
from unittest.mock import MagicMock, patch
from sitemanager.aws import S3Client

from sitemanager.config import AWSConfig
from tests.fakes import fake_aws_config, random_datetime, random_string


class S3ClientTests(TestCase):

    @patch("boto3.resource")
    def test_detects_bucket_exists(self, mock_boto_resource):
        """
        Detects that the s# bucket already exists by checking its creation date.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = random_datetime()

        result = S3Client(config, bucket_name).bucket_exists()

        self.assertTrue(result)

    @patch("boto3.resource")
    def test_detects_bucket_does_not_exist(self, mock_boto_resource):
        """
        Detects that the s# bucket doesn't exist by checking its creation date.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = None

        result = S3Client(config, bucket_name).bucket_exists()

        self.assertFalse(result)

    @patch("boto3.resource")
    def test_creates_bucket(self, mock_boto_resource):
        """
        Creates the bucket when it doesn't already exist.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = None

        S3Client(config, bucket_name).create_bucket()

        mock_bucket.create.assert_called_with(
            ACL='private',
            CreateBucketConfiguration={
                'LocationConstraint': config["region"]
            },
        )

    @patch("boto3.resource")
    def test_skips_creating_bucket_when_bucket_exists(self, mock_boto_resource):
        """
        Skips creating the bucket when it already exists.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = None

        S3Client(config, bucket_name).create_bucket()

        mock_bucket.create.assert_called_with(
            ACL='private',
            CreateBucketConfiguration={
                'LocationConstraint': config["region"]
            },
        )

    @patch("boto3.resource")
    def test_deletes_bucket(self, mock_boto_resource):
        """
        Deletes the bucket when it exists.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = random_datetime()

        S3Client(config, bucket_name).delete_bucket()

        mock_bucket.delete.assert_called_with()

    @patch("boto3.resource")
    def test_skips_deleting_nonexistent_bucket(self, mock_boto_resource):
        """
        Skips deleting the bucket when it doesn't exist.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.creation_date = None

        S3Client(config, bucket_name).delete_bucket()

        mock_bucket.delete.assert_not_called()

    @patch("boto3.resource")
    def test_gets_number_of_archives_in_bucket(self, mock_boto_resource):
        """
        Gets the number of archives in the bucket.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_object = MagicMock()
        mock_object.size = 1
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.objects.all.return_value = []

        for object_count in range(1, 5):
            mock_bucket.objects.all.return_value += [mock_object]
            result = S3Client(config, bucket_name).get_bucket_stats()
            self.assertEqual(result["archive_count"], object_count)

    @patch("boto3.resource")
    def test_gets_size_of_bucket(self, mock_boto_resource):
        """
        Gets the size of the bucket.
        """
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_object = MagicMock()
        object_size = random.randint(2, 10)
        mock_object.size = object_size
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value
        mock_bucket.objects.all.return_value = []

        for object_count in range(1, 5):
            mock_bucket.objects.all.return_value += [mock_object]
            result = S3Client(config, bucket_name).get_bucket_stats()
            self.assertEqual(result["total_size"], object_size * object_count)

    @patch("boto3.resource")
    def test_uploads_archive_to_bucket(self, mock_boto_resource):
        """
        Uploads file to S3 Bucket.
        """
        filename = f"{random_string(10)}.tar.gz"
        filepath = f"{random_string(10)}/{filename}"
        config = fake_aws_config()
        bucket_name = random_string(20)
        mock_object = MagicMock()
        mock_bucket = mock_boto_resource.return_value.Bucket.return_value

        S3Client(config, bucket_name).upload_archive_to_bucket(filepath)

        mock_bucket.upload_file.assert_called_with(filepath, filename)


if __name__ == "__main__":
    unittest.main()
