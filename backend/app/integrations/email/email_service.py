
import smtplib
from email.message import EmailMessage

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def send_email(
    recipient: str,
    subject: str,
    body: str,
    html: bool = False,
) -> bool:
    """Send an email using configured SMTP credentials."""

    if not settings.SMTP_HOST or not settings.EMAIL_FROM:
        logger.warning("Email service is not configured.")
        return False

    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials are missing.")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.EMAIL_FROM
    message["To"] = recipient

    if html:
        message.set_content("Please view this email in an HTML-compatible email client.")
        message.add_alternative(body, subtype="html")
    else:
        message.set_content(body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as server:
            server.starttls()
            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD,
            )
            server.send_message(message)

        logger.info("Email sent successfully to %s", recipient)
        return True

    except (smtplib.SMTPException, OSError):
        logger.exception("Failed to send email to %s", recipient)
        return False
