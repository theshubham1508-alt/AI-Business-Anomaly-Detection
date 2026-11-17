import os
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)


def send_email(summary, recipient_email=None):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    receiver_email = recipient_email or os.getenv("RECEIVER_EMAIL")

    print("\n" + "=" * 50)
    print("AUTOMATIC EMAIL REPORT")
    print("=" * 50)

    if not all([sender_email, app_password, receiver_email]):
        print("Email skipped: Credentials not configured in .env")
        return False

    message = MIMEText(str(summary), "plain", "utf-8")

    message["Subject"] = "AI Business Anomaly Detection Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=30
        ) as server:

            server.login(sender_email, app_password)
            server.send_message(message)

        print("Email Sent Successfully!")
        print(f"Report sent to: {receiver_email}")

        return True

    except Exception as e:
        print("Email Error:", e)
        return False