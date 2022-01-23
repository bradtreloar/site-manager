
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import sitemanager
from sitemanager.notifications.mail import Mailer, load_template, render_template
from tests import TestCaseWithConfig
from tests.fakes import random_string


class MailerTests(TestCaseWithConfig):

    def test_init(self):
        """
        Initialises with
        """
        mail_config = self.config["mail"]
        mailer = Mailer(mail_config)
        self.assertEqual(mailer.host, mail_config["host"])
        self.assertEqual(mailer.port, mail_config["port"])
        self.assertEqual(mailer.username, mail_config["username"])
        self.assertEqual(mailer.password, mail_config["password"])
        self.assertEqual(mailer.mail_from, mail_config["from"])
        self.assertEqual(mailer.mail_to, mail_config["to"])
        self.assertEqual(mailer.use_tls, mail_config["use_tls"])

    @patch('smtplib.SMTP', autospec=True)
    def test_notify_without_tls(self, mock_SMTP):
        """
        Sends message over unencrypted connection.
        """
        message_subject = random_string(20)
        message_body = random_string(20)
        mail_config = self.config["mail"]
        mail_config["use_tls"] = False
        mailer = Mailer(mail_config)
        mock_smtp = MagicMock()
        mock_SMTP.return_value.__enter__.return_value = mock_smtp
        mailer.notify(message_subject, message_body)
        mock_SMTP.assert_called_with(
            host=mailer.host,
            port=mailer.port)
        mock_smtp.login.assert_called()
        mock_smtp.sendmail.assert_called()

    @patch('ssl.create_default_context', autospec=True)
    @patch('smtplib.SMTP_SSL', autospec=True)
    def test_notify_without_tls(
            self, mock_SMTP_SSL, mock_create_default_context):
        """
        Sends message over encrypted connection.
        """
        message_subject = random_string(20)
        message_body = random_string(20)
        mail_config = self.config["mail"]
        mail_config["use_tls"] = True
        mailer = Mailer(mail_config)
        mock_smtp = MagicMock()
        mock_SMTP_SSL.return_value.__enter__.return_value = mock_smtp
        mailer.notify(message_subject, message_body)
        mock_SMTP_SSL.assert_called_with(
            host=mailer.host,
            port=mailer.port,
            context=mock_create_default_context.return_value)
        mock_smtp.login.assert_called()
        mock_smtp.sendmail.assert_called()

    @patch('builtins.open')
    @patch('os.path.exists')
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
                siteman_path, "notifications", "templates",
                module_name, f"{base_name}.html.j2")
            mock_os_path_exists.side_effect = [False, True]
            result = load_template(template_name)
            mock_os_path_exists.assert_called_with(template_path)
            mock_open.assert_called_with(template_path)
            self.assertEqual(result, mock_file.read.return_value)

    @patch('sitemanager.notifications.mail.Environment')
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
