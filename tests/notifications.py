
import os
from unittest import TestCase
import unittest
from unittest.mock import MagicMock, patch

import sitemanager
from sitemanager.templates.render import load_template, render_template
from tests import TestCaseWithConfig
from tests.fakes import random_string


class TemplateTests(TestCase):

    @patch("builtins.open")
    @patch("os.path.exists")
    def test_load_template(self, mock_os_path_exists, mock_open):
        """
        Reads the contents of a template file given the template name.
        """
        # Construct a fake template name.
        siteman_path = sitemanager.__path__[0]
        module_name = random_string(10)
        base_name = random_string(10)
        template_name = f"{module_name}.{base_name}"

        # Mock a file object to return the template contents when read.
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Test the first template path for the given template name.
        # "sitemanager/<module_name>/templates/base_name.html.j2"
        with patch('os.path.exists') as mock_os_path_exists:
            template_path = os.path.join(
                siteman_path, module_name, "templates", f"{base_name}.html.j2")
            mock_os_path_exists.side_effect = [True]
            result = load_template(template_name)
            mock_os_path_exists.assert_called_with(template_path)
            mock_open.assert_called_with(template_path)
            self.assertEqual(result, mock_file.read.return_value)

        # Test the second template path for the given template name.
        # "sitemanager/notifications/templates/[<module_name>/]base_name.html.j2"
        with patch('os.path.exists') as mock_os_path_exists:
            template_path = os.path.join(
                siteman_path, "templates", "common",
                module_name, f"{base_name}.html.j2")
            mock_os_path_exists.side_effect = [False, True]
            result = load_template(template_name)
            mock_os_path_exists.assert_called_with(template_path)
            mock_open.assert_called_with(template_path)
            self.assertEqual(result, mock_file.read.return_value)

    @patch("sitemanager.templates.render.Environment")
    def test_render_template(self, mock_Environment):
        """
        Loads and renders template with given data.
        """
        data = {
            random_string(10): random_string(20),
            random_string(10): random_string(20),
        }
        template_name = f"{random_string(10)}.{random_string(10)}"
        mock_template = MagicMock()
        mock_environment = MagicMock()
        mock_environment.get_template.return_value = mock_template
        mock_Environment.return_value = mock_environment
        result = render_template(template_name, data)
        self.assertEqual(result, mock_template.render.return_value)
        mock_environment.get_template.assert_called_with(template_name)
        mock_template.render.assert_called_with(**data)


if __name__ == "__main__":
    unittest.main()
