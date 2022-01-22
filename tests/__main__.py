
import unittest

from tests.commands import CommandTests
from tests.sites import SiteTests


TESTCASES = {
    CommandTests,
    SiteTests
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
