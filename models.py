# from sqlalchemy import Column, Integer, String, Boolean, DateTime
# from database import Base
# import datetime

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)

# class Order(Base):
#     __tablename__ = "orders"
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String)
#     cin = Column(String)
#     client_id = Column(String)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)
#     document_status = Column(String, default="pending")
#     zip_url = Column(String, nullable=True)
#     mail_sent = Column(Boolean, default=False)



from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    cin = Column(String)
    client_id = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    document_status = Column(String, default="pending")
    zip_url = Column(String, nullable=True)
    zip_created_at = Column(DateTime, nullable=True)  # ✅ NEW
    mail_sent = Column(Boolean, default=False)
    payment_id = Column(String, nullable=True)  # Razorpay payment ID
    refunded = Column(Boolean, default=False)

# models.py
class OTPRequest(Base):
    __tablename__ = "otp_requests"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

