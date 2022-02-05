
from unittest import TestCase

from sitemanager.database import BaseModel, get_db_session
from sitemanager.sites import import_sites
from sitemanager.models import Site, SiteSSH
from tests import TestCaseWithDatabase
from tests.fakes import fake_config, fake_site, fake_site_ssh, random_string


class SiteTests(TestCaseWithDatabase):

    def test_imports_site_from_config(self):
        """
        Imports Site from config.
        """
        site = fake_site()
        sites_config = {
            site.host: {}
        }
        webauth_config = {}
        import_sites(sites_config, webauth_config, self.db_session)
        sites = self.db_session.query(Site).all()
        self.assertEqual(sites[0].host, site.host)

    def test_activates_site_from_config(self):
        """
        Sets existing Site as active when imported from config.
        """
        site = fake_site({
            "is_active": False,
        })
        self.seed([
            site
        ])
        sites_config = {
            site.host: {}
        }
        webauth_config = {}
        self.assertFalse(site.is_active)
        import_sites(sites_config, webauth_config, self.db_session)
        sites = self.db_session.query(Site).all()
        self.assertEqual(sites[0].host, site.host)
        self.assertTrue(sites[0].is_active)

    def test_deactivates_site_missing_from_config(self):
        """
        Sets existing Site as inactive when missing from imported config.
        """
        site = fake_site({
            "is_active": True,
        })
        self.seed([
            site
        ])
        sites_config = {}
        webauth_config = {}
        self.assertTrue(site.is_active)
        import_sites(sites_config, webauth_config, self.db_session)
        sites = self.db_session.query(Site).all()
        self.assertEqual(sites[0].host, site.host)
        self.assertFalse(sites[0].is_active)

    def test_imports_ssh_config_from_config(self):
        """
        Imports SiteSSHConfig from config.
        """
        site = fake_site()
        ssh_config = fake_site_ssh(site)
        sites_config = {
            site.host: {
                "ssh": {
                    "host": ssh_config.host,
                    "port": ssh_config.port,
                    "user": ssh_config.user,
                    "key_filename": ssh_config.key_filename,
                },
            }
        }
        webauth_config = {}
        import_sites(sites_config, webauth_config, self.db_session)
        ssh_configs = self.db_session.query(SiteSSH).all()
        self.assertEqual(ssh_configs[0].host, ssh_config.host)
        self.assertEqual(ssh_configs[0].port, ssh_config.port)
        self.assertEqual(ssh_configs[0].user, ssh_config.user)
        self.assertEqual(ssh_configs[0].key_filename, ssh_config.key_filename)
