
import unittest

from tests.archive import ArchiveTests
from tests.backup import BackupTests
from tests.commands import CommandTests
from tests.config import ConfigTests
from tests.mail import MailerTests
from tests.monitoring import MonitoringTests, AsyncMonitoringTests
from tests.notifications import TemplateTests
from tests.sites import SiteTests


TESTCASES = {
    ArchiveTests,
    BackupTests,
    CommandTests,
    ConfigTests,
    MailerTests,
    MonitoringTests,
    AsyncMonitoringTests,
    SiteTests,
    TemplateTests
}


def main():
    """Run all tests."""
    testloader = unittest.TestLoader()
    testsuites = [
        testloader.loadTestsFromTestCase(testcase)
        for testcase in TESTCASES
    ]
    unittest.TextTestRunner(verbosity=2, buffer=True).run(
        unittest.TestSuite(testsuites))


if __name__ == "__main__":
    main()
