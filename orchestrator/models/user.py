from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean, LargeBinary
from datetime import datetime

class User(db.Model):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mpesa_number: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(15), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions = db.relationship("Subscription", backref="user", lazy=True)