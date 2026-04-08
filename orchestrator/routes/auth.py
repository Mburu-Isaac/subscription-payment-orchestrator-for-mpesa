from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from orchestrator.extensions import db
from orchestrator.models import User, OTP, PasswordHistory
from argon2.exceptions import VerifyMismatchError
from orchestrator.security.encryption import encrypt_contact
from orchestrator.security.hashing import hash_email, ph
from orchestrator.utilities.otps import manage_otp
from orchestrator.utilities.email.templates import otp_email, verification_email 
from datetime import datetime, timedelta
from orchestrator.utilities.slugify_utils import slugify_object
from orchestrator.utilities.user_login import log_in_user, authenticaticate_otp
from orchestrator.utilities.forward_otp import handle_otp_forwarding
from os import abort


bp = Blueprint("auth", __name__)

@bp.route("/signup", methods=["GET", "POST"])
def signup():  # add verification for signup 
            # authenticate via email 
                # ask user to allow autodetect and autofill code

            # start - build the pipeline
    if current_user.is_authenticated:
        return redirect(url_for("main.index_page"))

    if request.method == "POST":

        email = request.form.get("email")

        hashed_email = hash_email(email) 
        
        hashed_password = ph.hash(request.form.get("password"))

        user_records = db.session.execute(db.select(User)).scalars().all()

        email_records = [record.email for record in user_records]

        if hashed_email in email_records:
            flash("email already exists. Please login", "info")
            return redirect(url_for("auth.login"))

        else:

            try:
                username = request.form.get("username")
                slug = slugify_object(username)

                user = User(
                    mpesa_number=encrypt_contact(request.form.get("mpesa_number")),
                    user_name=username,
                    slug=slug,
                    email=hashed_email,
                    password=hashed_password,
                )

                password = PasswordHistory(user=user, password=hashed_password)

                db.session.add_all([user, password])
                db.session.commit()

                otp_type = "User Signup"

                result = handle_otp_forwarding(
                    user=user,
                    otp_type=otp_type,
                    email=email
                )

                otp_authentication = authenticaticate_otp(
                    result=result,
                    user=user
                )

                if otp_authentication is not None:
                    return otp_authentication

            except Exception:
                db.session.rollback()
                raise

            return redirect(
                url_for("auth.login")
            )  

    return render_template("signup.html", user=None)



# user signs up -> atp authentification -> email verification -> 
# -> update status to verified -> user logs out











@bp.route("/login", methods=["GET", "POST"])    # add 2-factor authentication 
def login():

    otp_type = request.args.get("otp_type")
    email = request.form.get("email")

    if current_user.is_authenticated:
        return redirect(url_for("main.index_page"))


    if request.method == "POST":

        user_object = db.session.execute(
            db.select(User).where(User.email == hash_email(email=email))
        ).scalar()

        if not user_object:
            flash("email does not exist. confirm email is correct|sign up", "info")
            return redirect(
                url_for(
                    "auth.login",
                    # otp_type=None
                )
            )  # add mechanism that allows the user to
            # head to signup page

        stored_password_hash = user_object.password
        password_attempt = request.form.get("password")

        try:
            ph.verify(stored_password_hash, password_attempt)

            decisive_otp_type = request.form.get("otp_type")

            if ph.check_needs_rehash(stored_password_hash):
                updated_password_hash = ph.hash(password_attempt)

                user_object.password = updated_password_hash
                db.session.commit()

            else:

                if decisive_otp_type == "user-signup":
                    user_logged_in = log_in_user(
                        user_object=user_object
                    )
                
                    if user_logged_in is not None:
                        return user_logged_in

                else:

                    otp_type = "Two Factor Authentication"

                     # generate OTP
                    result = handle_otp_forwarding(
                        user=user_object,
                        otp_type=otp_type,
                        email=email
                    )

                    # authenticate OTP
                    otp_authentication = authenticaticate_otp(
                        result=result,
                        user=user_object
                    )

                    # login user
                    if otp_authentication is not None:
                        return otp_authentication

        except VerifyMismatchError:
            flash("wrong password. please try again", "info")
            return redirect(url_for("auth.login"))

        except Exception:
            db.session.rollback()
            raise

    return render_template(
        "login.html",
         otp_type=otp_type
    )


@bp.route("/account-recovery/<slug>", methods=["GET", "POST"])
def account_recovery(slug):

    if current_user.is_authenticated:
        return redirect(url_for("main.index_page"))

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

        if not updated_password:
            flash("A password is required for password update")
            return redirect(url_for("auth.account_recovery", slug=user.slug))

        for password in password_records:
            try:
                ph.verify(password.password, updated_password)
                flash(
                    "password previously used. create a new password", "info"
                ) 

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

        flash("password was updated successfully", "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", user=user)


@bp.route("/recovery-email", methods=["GET", "POST"])
def get_email():

    if current_user.is_authenticated:
        return redirect(url_for("main.index_page"))

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

        else:

            otp_type = "Password Reset"

            result = handle_otp_forwarding(
                user=user,
                otp_type=otp_type,
                email=email
            )

            otp_authentication = authenticaticate_otp(
                result=result,
                user=user
            )

            if otp_authentication is not None:
                return otp_authentication
            


    return render_template("email.html")


@bp.route("/otp-verification/<slug>/<otp_type>", methods=["GET", "POST"])
def otp_verification(slug, otp_type):

    if current_user.is_authenticated:
        return redirect(url_for("main.index_page"))

    user = db.session.execute(
        db.select(User).where(User.slug == slug)
    ).scalar()

    user_id = user.id

    if not user:
        abort(404)

    if request.method == "POST":

        otp_attempt = request.form.get("otp")

        if otp_attempt is None:
            otp_attempt = ""

        otp_record = db.session.execute(
                db.select(OTP)
                .where(
                    OTP.user_id == user_id,
                    OTP.otp_type == otp_type
                )
            ).scalars().first()

        if not otp_record:
            flash("Enter OTP to proceed", "info")
            return redirect(
                url_for(
                    "auth.otp_verification",
                    slug=user.slug,
                    otp_type=otp_type
                )
            )

        else:
            return manage_otp(
                otp_record=otp_record,
                otp_attempt=otp_attempt,
                user=user,
                otp_type=otp_type
            )

    return render_template(
        "login.html",
        user=user,
        otp_type=otp_type
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index_page"))
