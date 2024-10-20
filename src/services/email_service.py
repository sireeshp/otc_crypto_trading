from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from src.models.EmailModel import EmailModel
from src.utils.config import Config
from src.utils.logger import setup_logger

logger = setup_logger("email_service", "logs/email_service.log")


def send_email(email: EmailModel):
    message = Mail(
        from_email=email.from_email or Config.FROM_EMAIL,
        to_emails=email.to,
        subject=email.subject,
        plain_text_content=email.plain_text_content,
        html_content=email.html_content,
    )
    try:
        sg = SendGridAPIClient(Config.SENDGRID_API_KEY)
        return sg.send(message)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
