from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Float
from datetime import datetime

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