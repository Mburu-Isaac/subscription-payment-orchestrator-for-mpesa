# Handle user creation - signup
# Handle user authentication - login

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user

from orchestrator.extensions import db
from orchestrator.models import User
from argon2.exceptions import VerifyMismatchError
from orchestrator.security.encryption import encrypt_contact
from orchestrator.security.hashing import hash_email,ph

bp = Blueprint("user", __name__)

@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = User(
            mpesa_number=encrypt_contact(request.form.get("mpesa_number")),
            user_name=request.form.get("username"),
            email=hash_email(request.form.get("email")),
            password=ph.hash(request.form.get("password"))
        )
        try:
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        login_user(user)
        #log in user before redirect
        return redirect(url_for("subscription.create_subscription")) # redirect to dashboard after creation
    return render_template("signup.html")

@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_object = db.session.execute(
            db.select(User).where(
                User.email == hash_email(request.form["email"])
            )
        ).scalar()

        stored_hash = user_object.password
        password_attempt = request.form["password"]

        if not user_object:
            flash("Invalid email.Try again", "danger")
            return redirect(url_for("user.login"))

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
            return redirect(url_for("subscription.subscription_index")) # create a dashboard
                                                                        # list of what users can do subscriptions|transactions|profile
        except VerifyMismatchError:
            flash("Invalid Password - return to login page", "danger")

    return render_template("login.html")

@bp.route("/update")
@login_required
def update_details():
    # user changes their transaction number here
    return "route allows users to update their details"

@bp.route("/profile")
@login_required
def user_profile():
    return"displays user profile"

@bp.route("/delete-account")
@login_required
def delete():
    return "route deletes user account"

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("user.login"))