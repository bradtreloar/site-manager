
import unittest

from tests.backup import BackupTests
from tests.commands import CommandTests
from tests.config import ConfigTests
from tests.notifications import MailerTests, TemplateTests
from tests.sites import SiteTests


TESTCASES = {
    BackupTests,
    CommandTests,
    ConfigTests,
    MailerTests,
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
