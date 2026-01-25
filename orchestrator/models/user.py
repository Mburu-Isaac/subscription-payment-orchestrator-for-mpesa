from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean
from datetime import datetime

class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mpesa_number: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions = db.relationship("Subscription", backref="user", lazy=True)