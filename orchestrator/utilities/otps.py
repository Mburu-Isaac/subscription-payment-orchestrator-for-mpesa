import secrets
import os
from dotenv import load_dotenv
from orchestrator.extensions import db
from orchestrator.models import OTP
from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash

load_dotenv()

def generate_otp(length=6):
    return ''.join(secrets.choice(os.getenv("OTP_SECRETS")) for _ in range(length))

def manage_otp(
    otp_record,
    otp_attempt,
    user, 
    otp_type
):

    expired_otps = db.session.execute(
        db.select(OTP).where(
            OTP.user_id == user.id,
            OTP.expires_at < datetime.now(timezone.utc)
        )
    ).scalars().all()

    try:

        if expired_otps:
            for otp in expired_otps:                                 
                db.session.delete(otp)

        current_time = datetime.now(timezone.utc)
        if current_time > otp_record.expires_at: #  add mechanism to regenrate code - 
                                                        # user sends a resend code request
                                                            # system regenerates and resends the code
            db.session.delete(otp_record)
            db.session.commit()
            flash("OTP expired. enter email to regenrate code", "info") 
            return render_template("email.html")

        elif check_password_hash(otp_record.hashed_otp, otp_attempt):

            # return render_template(
            #         "signup.html",
            #         user=user
            #     )

            

            if otp_type.lower() == "password-reset":
                return render_template(
                    "signup.html",
                    user=user
                )

            if otp_type.lower() == "user-signup":
                flash("Sign up was successful. Proceed to login", "success")
                return redirect(
                    url_for("auth.login")
                )

            # if otp_type == "Login-Verification":
            #     return redirect(
            #         url_for("main.index_page")
            #     )

            # if otp_type == "Manual-Transaction":
            #     pass

        else:

            if otp_record.attempts_left <= 1:
                flash("maximum OTP attempts reached, enter email to regenerate code", "info")
                db.session.delete(otp_record)
                db.session.commit()
                return render_template("email.html")

            else:
                otp_record.attempts_left -= 1
                db.session.commit()
                flash(f"invalid OTP. You have {otp_record.attempts_left} attempts left", "info")
                return render_template(
                    "login.html",
                    user=user
                )


    except Exception:
        db.session.rollback()
        raise


