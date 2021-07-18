

from manager.remote.client import RemoteCommandError


def exists(client, path):
    try:
        client.exec_command("stat {}".format(path))
    except RemoteCommandError:
        return False
    return True
