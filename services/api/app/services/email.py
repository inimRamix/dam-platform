from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings


async def send_email(to: str, subject: str, body: str):
    message = MIMEText(body, "html")
    message["From"] = settings.smtp.from_email
    message["To"] = to
    message["Subject"] = subject

    await aiosmtplib.send(
        message,
        hostname=settings.smtp.host,
        port=settings.smtp.port,
        username=settings.smtp.username,
        password=settings.smtp.password,
        use_tls=False,
    )
