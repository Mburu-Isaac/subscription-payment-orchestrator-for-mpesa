from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String, DateTime, Boolean, ForeignKey
from datetime import datetime

from mpesa import Mpesa

app = Flask(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///subscriptions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)

class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mpesa_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions = db.relationship("Subscription", backref="user", lazy=True)

class Subscription(db.Model):

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    service_name: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_type: Mapped[str] = mapped_column(String, nullable=False) #Paybill|Till Number
    till_number: Mapped[str] = mapped_column(String(30), nullable=True, unique=True)
    paybill_number: Mapped[str] = mapped_column(String(30), nullable=True, unique=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String, nullable=False)
    next_payment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active") #active|paused
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transactions = db.relationship("Transaction", backref="subscription", lazy=True)

class Transaction(db.Model):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending") #Pending|Success|Fail
    checkout_request_id: Mapped[str] = mapped_column(String, nullable=True)
    mpesa_receipt_number: Mapped[str] = mapped_column(String, nullable=True)
    failure_reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# with app.app_context():
#     db.create_all()

# transaction = Mpesa()
# print(transaction.token_cache())
# print(transaction.stk_push())







