from orchestrator.extensions import db
from sqlalchemy.orm import Mapped, mapped_column, backref
from sqlalchemy import Integer, String, DateTime, Boolean, LargeBinary
from datetime import datetime
from orchestrator.extensions import login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mpesa_number: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    user_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions = db.relationship("Subscription", backref="user", lazy=True)
    otps = db.relationship("OTP", backref="auth_user", lazy=True)
    password_history = db.relationship("PasswordHistory", backref="user", lazy=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))