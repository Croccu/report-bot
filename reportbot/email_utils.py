import os
import smtplib
from email.message import EmailMessage
from typing import Iterable, Optional

SMTP_HOST = os.getenv("REPORTBOT_SMTP_HOST")
SMTP_PORT = int(os.getenv("REPORTBOT_SMTP_PORT", "587"))
SMTP_USER = os.getenv("REPORTBOT_SMTP_USER")
SMTP_PASSWORD = os.getenv("REPORTBOT_SMTP_PASSWORD")
EMAIL_FROM = os.getenv("REPORTBOT_EMAIL_FROM")
EMAIL_TO_DEFAULT = os.getenv("REPORTBOT_EMAIL_TO")


# uses basic SMTP configuration from environment variables
# if email settings are missing, it logs a message and returns without raising
def send_report_email(
    subject: str,
    body: str,
    to_addrs: Optional[Iterable[str]] = None,
    reply_to: Optional[str] = None,
) -> None:

    if not SMTP_HOST or not EMAIL_FROM:
        print("Email not sent: REPORTBOT_SMTP_HOST or REPORTBOT_EMAIL_FROM not configured.")
        return

    recipients = list(to_addrs) if to_addrs else []
    if not recipients and EMAIL_TO_DEFAULT:
        recipients = [EMAIL_TO_DEFAULT]

    if not recipients:
        print("Email not sent: no recipients configured (REPORTBOT_EMAIL_TO or to_addrs).")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = ", ".join(recipients)
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            # Upgrade to TLS
            try:
                server.starttls()
            except Exception:
                # Some servers may not support STARTTLS; ignore if it fails.
                pass

            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)

            server.send_message(msg)

        print(f"Report email sent to: {', '.join(recipients)}")
    except Exception as e:
        print(f"Error sending report email: {e}")
