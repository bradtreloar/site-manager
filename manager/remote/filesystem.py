

from manager.remote.client import RemoteCommandError


def exists(client, path):
    try:
        client.exec_command("stat {}".format(path))
    except RemoteCommandError:
        return False
    return True


def ls(client, path):
    return client.exec_command(
        "ls wordpress/web/app/uploads").split("\n")
