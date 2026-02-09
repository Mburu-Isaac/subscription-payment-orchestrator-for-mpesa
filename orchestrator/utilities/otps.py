import secrets
import os
from dotenv import load_dotenv
from orchestrator.extensions import db
from orchestrator.models import OTP
from datetime import datetime, timezone

load_dotenv()

def generate_otp(length=6):
    return ''.join(secrets.choice(os.getenv("OTP_SECRETS")) for _ in range(length))

def otp_cleanup():
    expired_otps = db.session.execute(
        db.select(OTP).where(
            OTP.expires_at < datetime.now(timezone.utc)
        )
    ).scalars().all()

    if expired_otps:
        for otp in expired_otps:
            try:
                db.session.delete(otp)
            except Exception:
                db.session.rollback()
                raise

        db.session.commit()

    return True