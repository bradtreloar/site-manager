

import os
import re
import shutil
from manager.remote.client import RemoteClient
from manager.remote.filesystem import exists, ls

IGNORED_FILES = ["php", "css", "js", "styles", "simpletest"]


class DrupalClient:

    def __init__(self, ssh_config, backup_bucket):
        self.remote_client = RemoteClient(ssh_config)
        self.backup_bucket = backup_bucket

    def exists(self):
        return exists(self.remote_client, "drupal")

    def version(self):
        status = self.remote_client.exec_command(
            "cd drupal && vendor/bin/drupal site:status")
        return status.split('\n')[1].strip().split(" ")[-1]

    def site_names(self):
        sites_filepath = "drupal/web/sites/sites.php"
        if not exists(self.remote_client, sites_filepath):
            return ['default']
        lines = self.remote_client.exec_command(
            "cat " + sites_filepath).split('\n')
        site_names = []
        for line in lines:
            pattern = r"""\$sites\[['"]{1}[^'"]{1,}['"]{1}\]\s{0,1}=\s{0,1}['"]{1}([^'"]{1,})['"]{1};"""
            matches = re.search(pattern, line.strip())
            if matches:
                site_name = matches[1]
                if site_name not in site_names:
                    site_names.append(site_name)
        return site_names

    def export_database(self, site_name, dirpath):
        filepath = dirpath + "/data/{}/drupal.sql".format(site_name)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        home_path = self.remote_client.exec_command("pwd")
        self.remote_client.exec_command(
            "mkdir -p {}/tmp".format(home_path))
        temporary_database_filepath = home_path + "/tmp/drupal.sql"
        alias = "@self" if site_name == "default" else "@" + site_name
        self.remote_client.exec_command(
            "cd drupal && vendor/bin/drupal database:dump --no-interaction --quiet --file {}".format(temporary_database_filepath))
        self.remote_client.download_file(temporary_database_filepath, filepath)
        self.remote_client.exec_command(
            "rm {}".format(temporary_database_filepath))

    def download_site_files(self, site_name, dirpath):
        files_path = "web/sites/{}/files".format(site_name)
        os.makedirs(os.path.join(dirpath, files_path), exist_ok=True)
        for filename in ls(self.remote_client, "drupal/" + files_path):
            if filename not in IGNORED_FILES:
                remote_path = "drupal/" + files_path + "/" + filename
                local_path = os.path.join(dirpath, files_path, filename)
                self.remote_client.download_file(remote_path, local_path)

    def start_webauth_session(self):
        self.remote_client.start_webauth_session()
