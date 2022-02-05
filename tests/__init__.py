
from unittest import TestCase

from sitemanager.database import BaseModel, get_db_session
from sitemanager.sites import import_sites, Site, SiteSSH
from tests.fakes import fake_config, fake_site, fake_site_ssh


class TestCaseWithConfig(TestCase):

    def setUp(self):
        super().setUp()
        self.config = fake_config()


class TestCaseWithDatabase(TestCaseWithConfig):

    def setUp(self):
        super().setUp()
        self.db_session = get_db_session(self.config["database"])

    def tearDown(self):
        self.clear_database()

    def seed(self, records):
        """
        Seed the database from a list of records.

        Params:
            The list of records to add.
        """
        for record in records:
            self.db_session.add(record)
        self.db_session.commit()

    def clear_database(self):
        """
        Remove all records from the database.
        """
        for tbl in reversed(BaseModel.metadata.sorted_tables):
            self.db_session.execute(tbl.delete())
        self.db_session.commit()
