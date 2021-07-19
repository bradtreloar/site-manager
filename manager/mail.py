
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Mailer:

    def __init__(self, config):
        self.host = config["host"]
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]
        self.mail_from = config["from"]
        self.mail_to = config["to"]
        self.use_tls = config["use_tls"]

    def notify(self, message_subject, message_body):
        message = MIMEMultipart()
        message["Subject"] = message_subject
        message["From"] = self.mail_from
        message["To"] = self.mail_to
        message.attach(MIMEText(message_body, "html"))
        if self.use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host=self.host, port=self.port, context=context) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(
                    self.mail_from, self.mail_to, message.as_string()
                )
        else:
            with smtplib.SMTP(host=self.host, port=self.port) as smtp:
                smtp.login(self.username, self.password)
                smtp.sendmail(
                    self.mail_from, self.mail_to, message.as_string()
                )
