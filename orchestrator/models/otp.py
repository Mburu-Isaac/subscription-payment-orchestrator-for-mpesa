from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime, Integer
from datetime import datetime

class OTP(db.Model):

    __tablename__ = "otps"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    hashed_otp: Mapped[str] = mapped_column(String(), nullable=False)
    otp_type: Mapped[str] = mapped_column(String(50), default="login")
    expires_at: Mapped[datetime] = mapped_column(DateTime) # nullable=False
    attempts_left: Mapped[int] = mapped_column(Integer, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

