
import os
import boto3

from sitemanager.config import AWSConfig


class S3Client:

    def __init__(self, config: AWSConfig, bucket_name: str):
        self.region = config["region"]
        s3 = boto3.resource(
            's3',
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"])
        self.bucket = s3.Bucket(bucket_name)

    def bucket_exists(self):
        return self.bucket.creation_date is not None

    def create_bucket(self):
        if not self.bucket_exists():
            self.bucket.create(
                ACL='private',
                CreateBucketConfiguration={
                    'LocationConstraint': self.region
                },
            )

    def delete_bucket(self):
        if self.bucket_exists():
            self.bucket.delete()

    def get_bucket_stats(self):
        total_size = 0
        archive_count = 0
        for object_summary in self.bucket.objects.all():
            total_size += object_summary.size
            archive_count += 1
        return {
            "archive_count": archive_count,
            "total_size": total_size,
        }

    def upload_archive_to_bucket(self, archive_filepath):
        filename = os.path.basename(archive_filepath)
        self.bucket.upload_file(archive_filepath, filename)
