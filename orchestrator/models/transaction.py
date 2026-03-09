from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, Float
from datetime import datetime, timezone
from sqlalchemy import text

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
    indempotency_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    payment_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  # Pending|Success|Fail
    checkout_request_id: Mapped[str] = mapped_column(String, nullable=True)
    mpesa_receipt_number: Mapped[str] = mapped_column(String, nullable=True)
    failure_reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    # scheduler logic
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default=text("0"),
        nullable=False
        )
    last_attempted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
