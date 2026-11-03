import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_email(summary):

    sender_email = os.getenv("SENDER_EMAIL")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    if not all([sender_email, app_password, receiver_email]):
        print("Email alert skipped: Credentials not configured.")
        return

    message = MIMEText(str(summary))
    message["Subject"] = "Business Anomaly Report"
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(message)

        print("Email Sent Successfully!")

    except Exception as e:
        print("Email Error:", e)
