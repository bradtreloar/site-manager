
from unittest import TestCase

from sitemanager.database import BaseModel, get_db_session
from sitemanager.sites import import_sites, Site, SiteSSHConfig
from tests import TestCaseWithDatabase
from tests.fakes import fake_config, fake_site, fake_site_ssh_config


class SiteTests(TestCaseWithDatabase):

    def test_import_sites(self):
        """
        Imports sites and site SSH configs from a config dictionary.
        """
        import_sites(self.config["sites"],
                     self.config["webauth"], self.session)
        self.assertEqual(len(self.session.query(Site).all()),
                         len(self.config["sites"]))
        self.assertGreater(len(self.session.query(SiteSSHConfig).all()), 0)

    def test_import_sites_with_existing(self):
        """
        Imports sites and site SSH configs from a config dictionary, and marks
        existing sites as inactive if they do not appear in the config.
        """
        seeded_site = fake_site()
        seeded_site_ssh_config = fake_site_ssh_config(seeded_site)
        self.seed([seeded_site, seeded_site_ssh_config])
        self.assertEqual(len(self.session.query(Site).all()), 1)
        import_sites(self.config["sites"],
                     self.config["webauth"], self.session)
        sites = self.session.query(Site).all()
        self.assertEqual(len(sites), len(self.config["sites"]) + 1)
        self.assertFalse(sites[0].is_active)
        for i in range(1, len(sites)):
            self.assertTrue(sites[i].is_active)
