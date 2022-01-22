
import io
import re
from unittest import TestCase
from unittest.mock import patch

from sitemanager.commands import Commands, commands


mock_config = {
    "mail": {
        "to": "recipient@example.com",
        "from": "sender@example.com",
        "host": "smtp.example.com",
        "port": "2525",
        "username": "example_username",
        "password": "example_password",
        "use_tls": "False",
    }
}


class CommandTests(TestCase):

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_help_command(self, mock_stdout):
        """
        Prints a list of available commands to the screen.
        """
        Commands.help(mock_config, None).execute()
        expected_output = [
            r"",
            r"Available commands:",
            r"",
        ] + [re.compile(f"{command.__name__}") for command in commands()]
        output = mock_stdout.getvalue().split("\n")
        for index, pattern in enumerate(expected_output):
            if pattern == "":
                self.assertEqual(output[index], pattern)
            else:
                self.assertRegex(output[index], pattern)
