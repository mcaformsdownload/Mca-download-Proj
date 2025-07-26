# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import List
# from database import SessionLocal
# from models import Order
# from auth_utils import get_current_user
# from datetime import datetime
# from emailer import send_order_received_email
# import os
# import requests
# import razorpay

# order_router = APIRouter()

# JWT_TOKEN = os.getenv("SUREPASS_TOKEN")
# SUREPASS_ORDER_API = "https://kyc-api.surepass.io/api/v1/mca-api/create-order"

# class CreateOrderRequest(BaseModel):
#     cin_list: List[str]
#     razorpay_id: str
#     email: str

# # Dependency to get DB
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
# RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# class RazorpayOrderRequest(BaseModel):
#     amount: int  # in INR, like 129, 159 etc.
#     currency: str = "INR"
#     receipt: str

# @order_router.post("/create-razorpay-order")
# def create_razorpay_order(data: RazorpayOrderRequest):
#     try:
#         order = razorpay_client.order.create({
#             "amount": data.amount,  # convert to paise
#             "currency": data.currency,
#             "receipt": data.receipt,
#             "payment_capture": 1
#         })
#         return order
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @order_router.post("/create-order")
# def create_order(
#     req: CreateOrderRequest,
#     db: Session = Depends(get_db)
# ):
#     created_orders = []

#     for cin in req.cin_list:
#         try:
#             response = requests.post(
#                 SUREPASS_ORDER_API,
#                 headers={
#                     "Authorization": f"Bearer {JWT_TOKEN}",
#                     "Content-Type": "application/json"
#                 },
#                 json={"entity_id": cin}
#             )
#             res_json = response.json()

#             if not res_json.get("success"):
#                 continue  # skip failed orders

#             client_id = res_json["data"]["client_id"]

#             # Save order to DB
#             order = Order(
#                 email=req.email,
#                 cin=cin,
#                 client_id=client_id,
#                 created_at=datetime.utcnow(),
#                 document_status="pending",
#                 zip_url=None,
#                 mail_sent=False
#             )
#             db.add(order)
#             db.commit()

#             # Send email confirmation
#             send_order_received_email(req.email, cin, req.razorpay_id)
#             created_orders.append(cin)

#         except Exception as e:
#             print(f"❌ Failed to process CIN {cin}: {e}")

#     return {"message": "Orders created", "processed": created_orders}


# @order_router.get("/orders")
# def get_orders(
#     db: Session = Depends(get_db),
#     current_user: str = Depends(get_current_user)
# ):
#     orders = db.query(Order).filter(Order.email == current_user).order_by(Order.created_at.desc()).all()

#     result = []
#     for o in orders:
#         result.append({
#             "cin": o.cin,
#             "status": o.document_status,
#             "created_at": o.created_at,
#             "zip_url": o.zip_url
#         })

#     return result






from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import SessionLocal
from models import Order
from auth_utils import get_current_user
from datetime import datetime, timedelta  # ✅ Add timedelta here
from emailer import send_order_received_email
import os
import requests
import razorpay

order_router = APIRouter()

JWT_TOKEN = os.getenv("SUREPASS_TOKEN")
SUREPASS_ORDER_API = "https://kyc-api.surepass.io/api/v1/mca-api/create-order"

class CreateOrderRequest(BaseModel):
    cin_list: List[str]
    razorpay_id: str
    email: str

# Dependency to get DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class RazorpayOrderRequest(BaseModel):
    amount: int  # in INR, like 129, 159 etc.
    currency: str = "INR"
    receipt: str

@order_router.post("/create-razorpay-order")
def create_razorpay_order(data: RazorpayOrderRequest):
    try:
        order = razorpay_client.order.create({
            "amount": data.amount,  # convert to paise
            "currency": data.currency,
            "receipt": data.receipt,
            "payment_capture": 1
        })
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@order_router.post("/create-order")
def create_order(
    req: CreateOrderRequest,
    db: Session = Depends(get_db)
):
    created_orders = []

    for cin in req.cin_list:
        try:
            response = requests.post(
                SUREPASS_ORDER_API,
                headers={
                    "Authorization": f"Bearer {JWT_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"entity_id": cin}
            )
            res_json = response.json()

            if not res_json.get("success"):
                continue  # skip failed orders

            client_id = res_json["data"]["client_id"]

            # Save order to DB
            order = Order(
                email=req.email,
                cin=cin,
                client_id=client_id,
                created_at=datetime.utcnow(),
                document_status="pending",
                zip_url=None,
                mail_sent=False,
                payment_id=req.razorpay_id
)

            db.add(order)
            db.commit()

            # Send email confirmation
            send_order_received_email(req.email, cin, req.razorpay_id)
            created_orders.append(cin)

        except Exception as e:
            print(f"❌ Failed to process CIN {cin}: {e}")

    return {"message": "Orders created", "processed": created_orders}


@order_router.get("/orders")
def get_orders(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    orders = db.query(Order).filter(Order.email == current_user).order_by(Order.created_at.desc()).all()

    result = []
    now = datetime.utcnow()
    for o in orders:
        expired = False
        if o.zip_url and o.zip_created_at:
            expired = now > o.zip_created_at + timedelta(days=2)

        result.append({
            "cin": o.cin,
            "status": o.document_status,
            "created_at": o.created_at,
            "zip_url": o.zip_url if not expired else None,  # Remove URL if expired
            "expired": expired
        })

    return result

