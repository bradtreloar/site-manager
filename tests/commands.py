
from unittest import TestCase

from sitemanager.commands import Commands


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

    def test_help_command(self):
        Commands.help(mock_config, None).execute()
