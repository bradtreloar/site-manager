from paramiko import AutoAddPolicy, SSHClient
from scp import SCPClient


def get_scp_client(hostname, username, password):
    ssh_client = get_ssh_client(hostname, username, password)
    scp_client = SCPClient(ssh_client.get_transport())
    return scp_client


def get_ssh_client(hostname, username, password):
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    ssh_client.connect(hostname, username=username, password=password)
    return ssh_client
