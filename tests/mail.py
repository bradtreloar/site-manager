
import os
from unittest.mock import MagicMock, patch

from sitemanager.mail import Mailer
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
    def test_notify_with_tls(
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
