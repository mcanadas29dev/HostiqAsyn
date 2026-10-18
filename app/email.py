from email.message import EmailMessage

import aiosmtplib

from app.config import settings


async def send_email(
    to: str,
    subject: str,
    body: str,
) -> None:
    """Envía un correo vía SMTP (Proton Mail Bridge en desarrollo)."""
    print(f"[EMAIL] From={settings.smtp_from} To={to}")
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,  # Proton Bridge no usa STARTTLS en local
       # validate_certs=False,  # Proton Bridge no usa certificados válidos en local
    )