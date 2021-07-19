

import os
from manager.remote.client import RemoteClient
from manager.remote.filesystem import exists, ls


class WordpressClient:

    def __init__(self, config, site):
        self.remote_client = RemoteClient(config["ssh"], site)
        self.site = site

    def exists(self):
        return exists(self.remote_client, "wordpress")

    def version(self):
        return self.remote_client.exec_command(
            "cd wordpress && vendor/bin/wp core version")

    def export_database(self, filepath):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        home_path = self.remote_client.exec_command("pwd")
        self.remote_client.exec_command(
            "mkdir -p {}/tmp".format(home_path))
        temporary_database_filepath = home_path + "/tmp/wordpress.sql"
        self.remote_client.exec_command(
            "cd wordpress && vendor/bin/wp db export {}".format(temporary_database_filepath))
        self.remote_client.download_file(temporary_database_filepath, filepath)
        self.remote_client.exec_command(
            "rm {}".format(temporary_database_filepath))

    def download_site_files(self, dirpath):
        uploads_path = "web/app/uploads"
        os.makedirs(os.path.join(dirpath, uploads_path), exist_ok=True)
        for filename in ls(self.remote_client, "wordpress/" + uploads_path):
            if filename != "cache":
                remote_path = "wordpress/" + uploads_path + "/" + filename
                local_path = os.path.join(dirpath, uploads_path, filename)
                self.remote_client.download_file(remote_path, local_path)
