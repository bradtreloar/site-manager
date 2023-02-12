
from dotenv import dotenv_values
from io import StringIO
import os
import re
import shutil
from sitemanager.remote.client import RemoteClient
from sitemanager.remote.filesystem import exists, ls


class DrupalClient:

    IGNORED_GENERATED_FILES = ["php", "css", "js", "styles", "simpletest"]

    def __init__(self, ssh_config):
        self.remote_client = RemoteClient(ssh_config)
        self.docroot = "drupal"
        self._sites_settings = None

    def exists(self):
        return exists(self.remote_client, self.docroot)

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

    @property
    def sites_settings(self):
        if not self._sites_settings:
            self._sites_settings = {}
            for site_name in self.site_names():
                self._sites_settings[site_name] = self.site_settings(site_name)
        return self._sites_settings

    def site_settings(self, site_name):
        dotenv = self.remote_client.exec_command("cat drupal/.env")
        settings = dotenv_values(stream=StringIO(dotenv))
        prefix = site_name.upper().replace(".", "_")
        return {
            "database": {
                "host": settings.get(prefix + "_DBHOST", "localhost"),
                "port": settings.get(prefix + "_DBPORT", "3306"),
                "database": settings[prefix + "_DBNAME"],
                "username": settings[prefix + "_DBUSER"],
                "password": settings[prefix + "_DBPASS"],
            }
        }

    def export_databases(self, dirpath):
        for site_name, site_settings in self.sites_settings.items():
            self.export_database(site_name, site_settings, dirpath)

    def export_database(self, site_name, site_settings, dirpath):
        filepath = dirpath + f"/data/{site_name}/drupal.sql"
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        home_path = self.remote_client.exec_command("pwd")
        self.remote_client.exec_command(f"mkdir -p {home_path}/tmp")
        temporary_database_filepath = f"{home_path}/tmp/drupal_{site_name}.sql"
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
        for site_name, site_settings in self.sites_settings.items():
            self.download_site_files(site_name, dirpath)

    def download_site_files(self, site_name, dirpath):
        files_path = f"web/sites/{site_name}/files"
        os.makedirs(os.path.join(dirpath, files_path), exist_ok=True)
        for filename in ls(self.remote_client, "drupal/" + files_path):
            if filename not in self.IGNORED_GENERATED_FILES:
                remote_path = "drupal/" + files_path + "/" + filename
                local_path = os.path.join(dirpath, files_path, filename)
                self.remote_client.download_file(remote_path, local_path)
