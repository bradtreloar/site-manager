

import os
import shutil
from manager.remote.client import RemoteClient
from manager.remote.filesystem import exists, ls

IGNORED_FILES = ["php", "css", "js"]


class DrupalClient:

    def __init__(self, config, site):
        self.remote_client = RemoteClient(config["ssh"], site)
        self.site = site

    def exists(self):
        return exists(self.remote_client, "drupal")

    def version(self):
        status = self.remote_client.exec_command(
            "cd drupal && vendor/bin/drupal site:status")
        return status.split('\n')[1].strip().split(" ")[-1]

    def export_database(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        home_path = self.remote_client.exec_command("pwd")
        self.remote_client.exec_command(
            "mkdir -p {}/tmp".format(home_path))
        temporary_database_filepath = home_path + "/tmp/drupal.sql"
        self.remote_client.exec_command(
            "cd drupal && vendor/bin/drupal database:dump --no-interaction --quiet --file {}".format(temporary_database_filepath))
        self.remote_client.download_file(temporary_database_filepath, filepath)
        self.remote_client.exec_command(
            "rm {}".format(temporary_database_filepath))

    def download_site_files(self, dirpath):
        files_path = "web/sites/default/files"
        os.makedirs(os.path.join(dirpath, files_path), exist_ok=True)
        for filename in ls(self.remote_client, "drupal/" + files_path):
            if filename not in IGNORED_FILES:
                remote_path = "drupal/" + files_path + "/" + filename
                local_path = os.path.join(dirpath, files_path, filename)
                self.remote_client.download_file(remote_path, local_path)
