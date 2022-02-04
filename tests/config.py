
from unittest import TestCase
from unittest.mock import patch, mock_open
import yaml

from sitemanager.config import load_config
from tests.fakes import fake_config, random_string


class ConfigTests(TestCase):

    def test_help_command(self):
        """
        Merges config from file with default config.
        """
        fake_filepath = random_string(10)
        mock_config = fake_config()
        mock_config_data = yaml.safe_dump(mock_config)
        with patch("builtins.open",
                   mock_open(read_data=mock_config_data)) as mk_open:
            result = load_config(fake_filepath)
            mk_open.assert_called_with(fake_filepath)
        self.assertDictEqual(result, mock_config)
