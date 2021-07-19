

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
        data = self.remote_client.exec_command(
            "cd wordpress && vendor/bin/wp db export -")
        with open(filepath, "w") as file:
            file.write(data)

    def download_site_files(self, dirpath):
        filenames = ls(self.remote_client, "wordpress/web/app/uploads")
        for filename in filenames:
            if filename != "cache":
                remote_path = "wordpress/web/app/uploads/" + filename
                local_path = os.path.join(dirpath, filename)
                self.remote_client.download_file(remote_path, local_path)
