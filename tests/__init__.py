
from unittest import TestCase

from sitemanager.database import BaseModel, get_db_session
from sitemanager.sites import import_sites, Site, SiteSSHConfig
from tests.fakes import fake_config, fake_site, fake_site_ssh_config


class TestCaseWithConfig(TestCase):

    def setUp(self):
        super().setUp()
        self.config = fake_config()


class TestCaseWithDatabase(TestCaseWithConfig):

    def setUp(self):
        super().setUp()
        self.session = get_db_session(self.config["database"])

    def tearDown(self):
        self.clear_database()

    def seed(self, records):
        """
        Seed the database from a list of records.

        Params:
            The list of records to add.
        """
        for record in records:
            self.session.add(record)
        self.session.commit()

    def clear_database(self):
        """
        Remove all records from the database.
        """
        for tbl in reversed(BaseModel.metadata.sorted_tables):
            self.session.execute(tbl.delete())
        self.session.commit()
