
from datetime import timedelta, timezone
import io

from httpx import Response
import respx
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from sitemanager.enums import SiteStatus, StatusLogType
from sitemanager.monitoring import check_https_status, print_https_status_list
from tests.fakes import fake_site, fake_status_log_entry, random_datetime
from tests import TestCaseWithDatabase


class AsyncMonitoringTests(IsolatedAsyncioTestCase):

    @respx.mock
    @patch("sitemanager.monitoring.datetime")
    async def test_check_https_status(self, mock_datetime):
        """
        Checks the site is responding to HTTPS requests.
        """
        fake_request_time = random_datetime()
        fake_start_at = fake_request_time + timedelta(seconds=1)
        fake_end_at = fake_start_at + timedelta(seconds=1)
        mock_datetime.now.site_effect = [
            fake_request_time,
            fake_start_at,
            fake_end_at,
        ]
        site = fake_site()
        url = f"https://{site.host}"
        mock_route = respx.get(url).mock(return_value=Response(200))
        await check_https_status(site)
        self.assertTrue(mock_route.called)


class MonitoringTests(TestCaseWithDatabase):

    @patch("sitemanager.monitoring.datetime")
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
