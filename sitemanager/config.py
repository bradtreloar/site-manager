
import os
from typing import Dict, TypedDict
import yaml


class AWSConfig(TypedDict):
    region: str
    aws_access_key_id: str
    aws_secret_access_key: str


class BackupConfig(TypedDict):
    filesystem: str
    path: str
    bucket: str


class DatabaseConfig(TypedDict):
    path: str


class LoggingConfig(TypedDict):
    path: str


class MailConfig(TypedDict):
    mail_to: str
    mail_from: str
    host: str
    port: int
    username: str
    password: str
    use_tls: bool


class MailserviceConfig(TypedDict):
    host: str
    access_key: str


class SiteSSHConfig(TypedDict):
    host: str
    port: int
    user: str


class SiteConfig(TypedDict):
    app: str
    ssh: SiteSSHConfig


class Config(TypedDict):
    aws: AWSConfig
    backup: BackupConfig
    database: DatabaseConfig
    logging: LoggingConfig
    mail: MailConfig
    mailservice: MailserviceConfig
    sites: Dict[str, SiteConfig]


def load_config(filepath: str) -> Config:
    with open(filepath) as file:
        return yaml.safe_load(file)
