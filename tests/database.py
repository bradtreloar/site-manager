from unittest import TestCase
import unittest
from unittest.mock import patch

from sitemanager.database import get_db_session
from tests.fakes import fake_config


class DatabaseTests(TestCase):

    @patch("sitemanager.database.sessionmaker")
    @patch("sitemanager.database.create_engine")
    @patch("os.path")
    def test_gets_sqlite_session(
            self, mock_os_path, mock_create_engine, mock_sessionmaker):
        """
        Gets an SQLite session.
        """
        config = {
            "path": ":memory:"
        }

        result = get_db_session(config)

        mock_create_engine.assert_called_with("sqlite+pysqlite:///:memory:")
        self.assertEqual(result, mock_sessionmaker.return_value.return_value)


if __name__ == "__main__":
    unittest.main()
