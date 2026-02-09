# prevent back tracking in specific routes throughout the project
# implement message flashing

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from orchestrator.extensions import db
from orchestrator.models import User, OTP, PasswordHistory
from argon2.exceptions import VerifyMismatchError
from orchestrator.security.encryption import encrypt_contact
from orchestrator.security.hashing import hash_email, ph
from orchestrator.utilities.otps import generate_otp, otp_cleanup
from orchestrator.utilities.notifications import send_verification_email
from datetime import datetime, timedelta
from orchestrator.utilities.slugify_utils import slugify_object

bp = Blueprint("auth", __name__)


@bp.route("/signup", methods=["GET", "POST"])
def signup():  # add verification for signup - reinforce authentication at signup?
    if request.method == "POST":

        email = hash_email(request.form.get("email")) 
        hashed_password = ph.hash(request.form.get("password"))

        user_records = db.session.execute(db.select(User)).scalars().all()

        email_records = [record.email for record in user_records]

        if email in email_records:
            flash("email already exists. proceed to login", "info")
            return redirect(url_for("auth.login"))
        else:

            username = request.form.get("username")
            slug = slugify_object(username)

            user = User(
                mpesa_number=encrypt_contact(request.form.get("mpesa_number")),
                user_name=username,
                slug=slug,
                email=email,
                password=hashed_password,
            )

            password = PasswordHistory(user=user, password=hashed_password)


            try:
                db.session.add_all([user, password])
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

            login_user(user)

            return redirect(
                url_for("subscription.create_subscription")
            )  # redirect to home page after creation
            # when user is freshly signed up
            # have "create subscriptions" of the three links alone
    return render_template("signup.html", user=None)


@bp.route("/login", methods=["GET", "POST"])
def login():

    # prevent user from backtracking to login page - current_user.is_authenticated

    if request.method == "POST":

        print(request.form.get("email"))

        user_object = db.session.execute(
            db.select(User).where(User.email == hash_email(request.form.get("email")))
        ).scalar()

        print(user_object)

        if not user_object:
            flash("email does not exist. confirm email is correct|sign up", "info")
            return redirect(
                url_for("auth.login")
            )  # add mechanism that allows the user to
            # head to signup page

        stored_hash = user_object.password
        password_attempt = request.form.get("password")

        try:
            ph.verify(stored_hash, password_attempt)

            if ph.check_needs_rehash(stored_hash):
                updated_hash = ph.hash(password_attempt)

                try:
                    user_object.password = updated_hash
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise
            login_user(user_object) 
            return redirect(
                url_for("subscription.subscription_index")
            )  # create a home page
            # list of what users can do subscriptions|transactions|profile
        except VerifyMismatchError:
            flash("wrong password. please try again", "info")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@bp.route("/account-recovery/<slug>", methods=["GET", "POST"])
def account_recovery(slug):

    user = db.session.execute(
        db.select(User).where(User.slug == slug)
    ).scalar()

    password_records = (
        db.session.execute(
            db.select(PasswordHistory).where(PasswordHistory.user_id == user.id)
        )
        .scalars()
        .all()
    )

    if request.method == "POST":

        updated_password = request.form.get("update_password")
        for password in password_records:
            try:
                ph.verify(password.password, updated_password)
                flash(
                    "password previously used. create a new password", "info"
                )  # inform them that the password they added has been used previously
                # advise them to use a unique password
                return redirect(url_for("auth.account_recovery", slug=user.slug))
                # add a back to login option in account recovery -
            # for when the user remembers their password when updating password

            except VerifyMismatchError:
                try:
                    user.password = ph.hash(updated_password)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise

        # add message to inform them that password was updated successfully
        flash("password was updated successfully", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", user=user)


@bp.route("/recovery-email", methods=["GET", "POST"])
def get_email():

    if request.method == "POST":
        email = request.form.get("email")

        user = db.session.execute(
            db.select(User).where(User.email == hash_email(email))
        ).scalar()

        if not user:
            flash(
                "email does not exist. confirm that the email entered is correct",
                "info",
            )
            return redirect(url_for("auth.get_mail"))

        otp = generate_otp()

        otp_record = OTP(
            user_id=user.id,
            hashed_otp=generate_password_hash(otp),
            otp_type="reset",
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            attempts_left=3,
        )

        try:
            db.session.add(otp_record)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        if send_verification_email(otp, email):
            return redirect(url_for("auth.otp_verification", slug=user.slug))

    return render_template("email.html")


@bp.route("/otp-verification/<slug>", methods=["GET", "POST"])
def otp_verification(slug):

    user = db.session.execute(
        db.select(User).where(User.slug == slug)
    ).scalar()

    user_id = user.id

    if request.method == "POST":

        otp_record = db.session.execute(
                db.select(OTP)
                .where(OTP.user_id == user_id)
                .order_by(OTP.created_at.desc())
            ).scalars().first()
        
        if otp_cleanup():

            if datetime.utcnow() > otp_record.expires_at:
                try:
                    db.session.delete(otp_record)
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise

                flash("OTP expired. enter email to regenerate code", "info")
                return redirect(url_for("auth.get_email"))  # inform user OTP expired

            if otp_record.attempts_left <= 0:
                try:
                    db.session.delete(otp_record)
                    db.session.commit()
                    return redirect(url_for("auth.get_email"))
                except Exception:
                    db.session.rollback()
                    raise

            if check_password_hash(otp_record.hashed_otp, request.form.get("otp")):
                return redirect(url_for("auth.account_recovery", slug=user.slug))
            else:
                try:
                    otp_record.attempts_left -= 1
                    db.session.commit()
                    flash(
                        f"invalid OTP. You have {otp_record.attempts_left} attempts left",
                        "info",
                    )  # inform user on the webpage
                    return redirect(url_for("auth.otp_verification", slug=user.slug))
                except Exception:
                    db.session.rollback()
                    raise

    return render_template("login.html", user=user)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
