
from datetime import timedelta, timezone
import io
from sitemanager.enums import SiteStatus, StatusLogType

from tests import TestCaseWithDatabase
from unittest.mock import patch

from sitemanager.monitoring import check_https_status, print_https_status_list
from tests.fakes import fake_site, fake_status_log_entry, random_datetime


class MonitoringTests(TestCaseWithDatabase):

    @patch('sitemanager.monitoring.datetime')
    def test_print_https_status_list(self, mock_datetime):
        """
        Displays website status for each site.
        """
        fake_now = random_datetime()
        mock_datetime.now.return_value = fake_now
        site = fake_site()
        status_age = timedelta(days=1)
        status_created = fake_now - status_age
        status_log_entry = fake_status_log_entry(site, {
            "type": StatusLogType.HTTPS,
            "status": SiteStatus.UP,
            "created": status_created,
        })
        self.seed([site, status_log_entry])

        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            print_https_status_list([site])
            output = mock_stdout.getvalue()
            self.assertIn(site.host, output)
            self.assertIn("UP", output)
