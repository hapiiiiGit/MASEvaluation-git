import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict


class EmailSender:
    def __init__(self, smtp_config: Dict):
        """
        smtp_config: dict with keys 'host', 'port', 'username', 'password'
        """
        self.host = smtp_config.get("host")
        self.port = smtp_config.get("port")
        self.username = smtp_config.get("username")
        self.password = smtp_config.get("password")
        self.use_tls = smtp_config.get("use_tls", True)

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email to the specified recipient.
        Returns True if sent successfully, False otherwise.
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.host, self.port, timeout=10)
            if self.use_tls:
                server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False