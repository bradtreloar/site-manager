
from unittest import TestCase
from unittest.mock import patch, mock_open
import yaml

from sitemanager.config import DEFAULT_CONFIG, load_config
from tests.fakes import fake_config, random_string


class ConfigTests(TestCase):

    def test_help_command(self):
        """
        Merges config from file with default config.
        """
        fake_filepath = random_string(10)
        mock_config = dict(DEFAULT_CONFIG)
        mock_config.update(fake_config())
        print(mock_config)
        mock_config_data = yaml.safe_dump(mock_config)
        with patch("builtins.open",
                   mock_open(read_data=mock_config_data)) as mock_file:
            result = load_config(fake_filepath)
            mock_file.assert_called_with(fake_filepath)
        self.assertDictEqual(result, mock_config)
