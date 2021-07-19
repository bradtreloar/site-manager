
import os
import boto3


class S3BackupBucketClient:

    def __init__(self, config, site):
        self.site = site
        self.region = config["region"]
        s3 = boto3.resource('s3',
                            aws_access_key_id=config["aws_access_key_id"],
                            aws_secret_access_key=config["aws_secret_access_key"])
        self.bucket = s3.Bucket("sitebackup-" + site["host"])

    def exists(self):
        return self.bucket.creation_date is not None

    def create(self):
        if not self.exists():
            self.bucket.create(
                ACL='private',
                CreateBucketConfiguration={
                    'LocationConstraint': self.region
                },
            )

    def delete(self):
        if self.exists():
            self.bucket.delete()

    def get_summary(self):
        total_size = 0
        archive_count = 0
        for object_summary in self.bucket.objects.all():
            total_size += object_summary.size
            archive_count += 1
        return {
            "archive_count": archive_count,
            "total_size": total_size,
        }

    def upload_archive(self, archive_filepath):
        filename = os.path.basename(archive_filepath)
        self.bucket.upload_file(archive_filepath, filename)
