import os
import logging
import smtplib
from typing import Optional
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    """
    Handles sending emails with PDF attachments to students.
    Uses SMTP (e.g., Gmail, Office365, or custom SMTP server).
    """

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        sender_name: str,
        sender_email: str,
        use_tls: bool = True
    ):
        """
        Initialize the EmailSender.

        Args:
            smtp_server (str): SMTP server address.
            smtp_port (int): SMTP server port.
            smtp_user (str): SMTP username.
            smtp_password (str): SMTP password.
            sender_name (str): Display name for sender.
            sender_email (str): Sender's email address.
            use_tls (bool): Whether to use TLS (default True).
        """
        self.logger = logging.getLogger("EmailSender")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.use_tls = use_tls

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        attachment: Optional[str] = None
    ):
        """
        Send an email with optional PDF attachment.

        Args:
            to (str): Recipient email address.
            subject (str): Email subject.
            body (str): Email body (plain text or HTML).
            attachment (Optional[str]): Path to PDF file to attach.

        Raises:
            Exception: If sending fails.
        """
        msg = MIMEMultipart()
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = to
        msg['Subject'] = subject

        # Attach the email body (HTML preferred)
        msg.attach(MIMEText(body, 'html'))

        # Attach the PDF if provided
        if attachment:
            if not os.path.isfile(attachment):
                self.logger.error(f"Attachment file not found: {attachment}")
                raise FileNotFoundError(f"Attachment file not found: {attachment}")
            try:
                with open(attachment, "rb") as f:
                    part = MIMEBase('application', 'pdf')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(attachment)}"'
                )
                msg.attach(part)
            except Exception as e:
                self.logger.error(f"Failed to attach PDF: {e}")
                raise

        # Send the email
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            self.logger.info(f"Email sent to {to} with subject '{subject}'")
        except Exception as e:
            self.logger.error(f"Failed to send email to {to}: {e}")
            raise