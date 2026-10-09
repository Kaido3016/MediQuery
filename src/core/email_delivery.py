"""Transactional email adapter. It never logs or returns account tokens."""

from email.message import EmailMessage
import smtplib
import ssl

from src.core.settings import get_settings


def send_account_email(recipient: str, subject: str, text_body: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        if settings.environment.lower() == "production":
            raise RuntimeError("Account email delivery is not configured")
        # Local development intentionally avoids exposing one-time tokens in logs.
        return
    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        server.starttls(context=context)
        if settings.smtp_username:
            server.login(settings.smtp_username, settings.smtp_password or "")
        server.send_message(message)
