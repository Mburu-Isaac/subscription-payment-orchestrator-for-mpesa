from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Float
from datetime import datetime, timezone

class Transaction(db.Model):

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subscription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "subscriptions.id"
        ),  # return the name of the subscription - transaction_object.subscription.name
        nullable=False,
    )
    slugify: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # slug = transaction_object.subscription.name - transaction_object.mpesa-receipt-number
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # Pending|Success|Fail
    checkout_request_id: Mapped[str] = mapped_column(String, nullable=True)
    mpesa_receipt_number: Mapped[str] = mapped_column(String, nullable=True)
    failure_reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
