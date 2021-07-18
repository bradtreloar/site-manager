from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient


class RemoteCommandError(BaseException):
    pass


class RemoteClient:

    def __init__(self, config, site):
        self.config = config
        self.site = site

    def get_scp_client(self):
        ssh_client = self.get_ssh_client()
        scp_client = SCPClient(ssh_client.get_transport())
        return scp_client

    def get_ssh_client(self):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(self.site["host"],
                           username=self.site["user"],
                           port=self.site["port"],
                           key_filename=self.config["key_filename"])
        return ssh_client

    def exec_command(self, command):
        ssh_client = self.get_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command(command)
        error = stderr.read().decode('utf8')
        stdin.close()
        ssh_client.close()
        if error:
            raise RemoteCommandError(error)
        return stdout.read().decode('utf8')
