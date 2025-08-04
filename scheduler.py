from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Order
from emailer import send_download_ready_email, send_order_failed_email
import requests
import os
from dotenv import load_dotenv
import datetime
import razorpay

load_dotenv()

SUREPASS_STATUS_API = "https://kyc-api.surepass.io/api/v1/mca-api/status/"
SUREPASS_TOKEN = os.getenv("SUREPASS_TOKEN")

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

scheduler = BackgroundScheduler()


def check_order_status():
    print("🔁 Checking order status...")

    db: Session = SessionLocal()
    try:
        pending_orders = db.query(Order).filter(Order.document_status == "pending").all()

        for order in pending_orders:
            if not order.client_id:
                continue

            try:
                res = requests.get(
                    f"{SUREPASS_STATUS_API}{order.client_id}",
                    headers={
                        "Authorization": f"Bearer {SUREPASS_TOKEN}",
                        "Content-Type": "application/json"
                    }
                )

                res_json = res.json()
                status = res_json["data"]["status"]

                if res_json.get("success"):
                    if status == "completed":
                        zip_url = res_json["data"]["zip"]["zip_url"]
                        order.document_status = "completed"
                        order.zip_url = zip_url
                        order.zip_created_at = datetime.datetime.utcnow()
                        order.mail_sent = True
                        db.commit()

                        send_download_ready_email(order.email, order.cin, zip_url)
                        print(f"✅ Order for {order.cin} marked completed and email sent")

                    elif status == "failed":
                        if not order.refunded:
                            try:
                                payment = razorpay_client.payment.fetch(order.payment_id)
                                refund_amount = payment["amount"]

                                razorpay_client.payment.refund(order.payment_id, {"amount": refund_amount})

                                order.document_status = "failed"
                                order.refunded = True
                                order.mail_sent = True
                                db.commit()

                                send_order_failed_email(order.email, order.cin)
                                print(f"❌ Order for {order.cin} failed. Refunded ₹{refund_amount / 100} and email sent")

                            except Exception as e:
                                print(f"❌ Refund failed for CIN {order.cin}: {e}")
                        else:
                            print(f"⚠️ Order for {order.cin} already refunded")

            except Exception as e:
                print(f"❌ Error checking status for {order.cin}: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(check_order_status, "interval", hours=3)
    scheduler.start()
