

from dotenv import dotenv_values
from io import StringIO
import os
from sitemanager.remote.client import RemoteClient
from sitemanager.remote.filesystem import exists, ls


class WordpressClient:

    IGNORED_GENERATED_FILES = {
        "cache"
    }

    def __init__(self, ssh_config):
        self.remote_client = RemoteClient(ssh_config)
        self.docroot = "wordpress"

    def exists(self):
        return exists(self.remote_client, self.docroot)

    def version(self):
        return self.remote_client.exec_command(
            f"cd {self.docroot} && vendor/bin/wp core version")

    def site_settings(self):
        dotenv = self.remote_client.exec_command(f"cat {self.docroot}/.env")
        settings = dotenv_values(stream=StringIO(dotenv))
        return {
            "database": {
                "host": settings.get("DB_HOST", "localhost"),
                "port": settings.get("DB_PORT", "3306"),
                "database": settings["DB_NAME"],
                "username": settings["DB_USER"],
                "password": settings["DB_PASSWORD"],
            }
        }

    def export_databases(self, dirpath):
        self.export_database(f"{dirpath}/data/wordpress.sql")

    def export_database(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        home_path = self.remote_client.exec_command("pwd")
        self.remote_client.exec_command(f"mkdir -p {home_path}/tmp")
        temporary_database_filepath = home_path + "/tmp/wordpress.sql"
        site_settings = self.site_settings()
        database_settings = site_settings["database"]
        command = "MYSQL_PWD='{password}' mysqldump --user='{username}' '{database}' > {file}".format(
            database=database_settings["database"],
            username=database_settings["username"],
            password=database_settings["password"],
            file=temporary_database_filepath
        )
        self.remote_client.exec_command(command)
        self.remote_client.download_file(temporary_database_filepath, filepath)
        self.remote_client.exec_command(f"rm {temporary_database_filepath}")

    def download_generated_files(self, dirpath):
        uploads_path = "web/app/uploads"
        os.makedirs(os.path.join(dirpath, uploads_path), exist_ok=True)
        for filename in ls(self.remote_client, "wordpress/" + uploads_path):
            if filename not in self.IGNORED_GENERATED_FILES:
                remote_path = f"{self.docroot}/{uploads_path}/{filename}"
                local_path = os.path.join(dirpath, uploads_path, filename)
                self.remote_client.download_file(remote_path, local_path)
