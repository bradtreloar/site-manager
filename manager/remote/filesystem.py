

from manager.remote.client import RemoteCommandError


def exists(client, path):
    try:
        client.exec_command(f"stat {path}")
    except RemoteCommandError:
        return False
    return True


def ls(client, dirpath):
    return client.exec_command(f"ls {dirpath}").split("\n")
