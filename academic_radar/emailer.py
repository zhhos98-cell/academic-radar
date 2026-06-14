import os
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText

from .render import render_email


def send_email(items, max_items):
    missing = [key for key in ["SMTP_USER", "SMTP_PASS", "TO_EMAIL"] if not os.environ.get(key)]
    if missing:
        raise RuntimeError(f"Missing email environment variables: {', '.join(missing)}")

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    msg = MIMEText(render_email(items, max_items), "html", "utf-8")
    msg["Subject"] = f"Daily Academic Radar - {today}"
    msg["From"] = os.environ["SMTP_USER"]
    msg["To"] = os.environ["TO_EMAIL"]

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
        smtp.send_message(msg)
