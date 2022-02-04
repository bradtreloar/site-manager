
from datetime import datetime
from random import randint, choice as random_choice
import string

from sitemanager.enums import SiteStatus, StatusLogType
from sitemanager.models import StatusLogEntry
from sitemanager.sites import Site, SiteSSHConfig


def random_string(length):
    return "".join(
        [random_choice(string.ascii_uppercase) for _ in range(length)])


def random_datetime(min=0, max=2000000000):
    return datetime.fromtimestamp(float(randint(min, max)))


def fake_config(config={}):
    default_config = {
        "database": {
            "path": ":memory:",
        },
        "sites": {
            "example1.com": {},
            "example2.com": {
                "app": "wordpress",
                "ssh": {
                    "user": "example2user",
                }
            },
            "example3.com": {
                "app": "wordpress",
                "ssh": {
                    "user": "example3user",
                    "host": "ssh.example3.com",
                    "port": "21212",
                    "key_filename": "/path/to/key_filename",
                }
            }
        },
        "aws": fake_aws_config(),
        "mail": {
            "to": "recipient@example.com",
            "from": "sender@example.com",
            "host": "smtp.example.com",
            "port": "2525",
            "username": "example_username",
            "password": "example_password",
            "use_tls": "False",
        },
        "webauth": {},
    }
    default_config.update(config)
    return default_config


def fake_aws_config(config={}):
    return {
        "region": random_string(20),
        "aws_access_key_id": random_string(20),
        "aws_secret_access_key": random_string(20),
    }


def fake_host():
    return "{}.com".format(
        ''.join(random_choice(
            string.ascii_letters) for x in range(randint(6, 12))))


def fake_site(values={}):
    return Site(
        host=values.get("host", fake_host()),
        is_active=values.get("is_active", True))


def fake_site_ssh_config(site, values={}):
    return SiteSSHConfig(
        site=site,
        host=values.get("host", fake_host()),
        port=values.get("port", 22),
        user=values.get("user", random_string(20)))


def fake_status_log_entry(site, values={}):
    return StatusLogEntry(
        site=site,
        type=values.get("type", StatusLogType.HTTPS),
        status=values.get("status", SiteStatus.UP),
        created=values.get("created", random_datetime()))
