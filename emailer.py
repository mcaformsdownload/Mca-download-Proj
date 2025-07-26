import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def send_order_received_email(to_email, cin, payment_id):
    try:
        subject = f"Order Received for CIN: {cin}"
        body = f"""
        Hi,

        We've received your order for CIN {cin}.
        Payment ID: {payment_id}

        We will notify you once the document is ready.

        Regards,
        MCA Docs Bot
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"📩 Order confirmation email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send confirmation email: {e}")


def send_download_ready_email(to_email, cin, zip_url):
    try:
        subject = f"Document Ready for CIN: {cin}"
        body = f"""
        Hi,

        Your MCA document for CIN {cin} is ready.
        The link will be expired within 2 days.

        Download ZIP: {zip_url}

        Regards,
        MCA Docs Bot
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"📩 Download ready email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send download email: {e}")

def send_otp_email(to_email, otp):
    try:
        subject = "Your OTP Code"
        body = f"""
        Hi,

        Your OTP is: {otp}
        It is valid for 10 minutes.

        MCA Docs Team
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"✅ OTP sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send OTP: {e}")


def send_order_failed_email(to_email, cin):
    try:
        subject = f"Order Failed for CIN: {cin}"
        body = f"""
        Hi,

        Unfortunately, we were unable to fetch the document for CIN {cin}.
        Your payment will be refunded automatically within 5-7 working days.

        You may try again later if needed.

        Regards,
        MCA Docs Bot
        """

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, to_email, msg.as_string())

        print(f"📩 Failure email sent to {to_email}")

    except Exception as e:
        print(f"❌ Failed to send failure email: {e}")

# ----------------25/07/25--------------------------------
def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, to_email, msg.as_string())

    print(f"📩 Email sent to {to_email}")
# --------------------------------------------------------
