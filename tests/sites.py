
from random import randint, choice as random_choice
import string
from unittest import TestCase

from sitemanager.database import get_db_session
from sitemanager.sites import import_sites, Site, SiteSSHConfig


def random_string(length):
    return "".join(
        [random_choice(string.ascii_uppercase) for _ in range(length)])


mock_database_config = {
    "path": ":memory:"
}


mock_sites_config = {
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
}


mock_webauth_config = {}


def clear_database(db_session):
    db_session.query(Site).delete()
    db_session.query(SiteSSHConfig).delete()


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


def seed_database(db_session, site_count):
    for _ in range(site_count):
        site = fake_site()
        site_ssh_config = fake_site_ssh_config(site)
        db_session.add(site)
        db_session.add(site_ssh_config)
    db_session.commit()


class CommandTests(TestCase):

    def test_import_sites(self):
        """
        Imports sites and site SSH configs from a config dictionary.
        """
        db_session = get_db_session(mock_database_config)
        import_sites(mock_sites_config, mock_webauth_config, db_session)
        self.assertEqual(len(db_session.query(Site).all()),
                         len(mock_sites_config))
        self.assertGreater(len(db_session.query(SiteSSHConfig).all()), 0)
        clear_database(db_session)

    def test_import_sites_with_existing(self):
        """
        Imports sites and site SSH configs from a config dictionary, and marks
        existing sites as inactive if they do not appear in the config.
        """
        db_session = get_db_session(mock_database_config)
        seed_database(db_session, 1)
        self.assertEqual(len(db_session.query(Site).all()), 1)
        import_sites(mock_sites_config, mock_webauth_config, db_session)
        sites = db_session.query(Site).all()
        self.assertEqual(len(sites), len(mock_sites_config) + 1)
        self.assertFalse(sites[0].is_active)
        for i in range(1, len(sites)):
            self.assertTrue(sites[i].is_active)
