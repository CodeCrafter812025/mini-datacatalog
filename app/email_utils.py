# app/email_utils.py
import os
import smtplib
from email.message import EmailMessage

def send_error_email(subject: str, body: str) -> None:
    host = os.getenv("SMTP_HOST", "localhost")
    port = int(os.getenv("SMTP_PORT", "1025"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_addr = os.getenv("SMTP_FROM", "dev@mini.local")
    to_addr = os.getenv("ERROR_NOTIFY_TO", "dev@mini.local")
    use_starttls = os.getenv("SMTP_STARTTLS", "false").lower() in ("1", "true", "yes")

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, port, timeout=10) as s:
        s.ehlo()
        if use_starttls:
            s.starttls()
            s.ehlo()
        if user and password:
            s.login(user, password)
        s.send_message(msg)
