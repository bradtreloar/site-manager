
import os

from datetime import datetime


class Logger:

    def __init__(self, config):
        self.path = config["path"]
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def log(self, message):
        with open(self.path, "a") as file:
            logged_at = datetime.now()
            file.write("{}\t{}\n".format(logged_at, message))
