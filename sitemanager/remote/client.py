
from abc import ABC
from requests.sessions import Session
import urllib3
import requests
from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'  # type: ignore


class RemoteCommandError(BaseException):
    pass


class RemoteClient(ABC):

    def __init__(self, config):
        self.config = config

    def get_scp_client(self):
        ssh_client = self.get_ssh_client()
        scp_client = SCPClient(ssh_client.get_transport())
        return scp_client

    def get_ssh_client(self):
        ssh_client = SSHClient()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(self.config["host"],
                           username=self.config["user"],
                           port=self.config["port"],
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
        return stdout.read().decode('utf8').strip()

    def download_file(self, src, dest):
        scp_client = self.get_scp_client()
        scp_client.get(src, dest, recursive=True)


class LoginError(BaseException):
    pass
