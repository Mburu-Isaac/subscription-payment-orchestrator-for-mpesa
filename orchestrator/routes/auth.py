# Handle user creation - signup
# Handle user authentication - login

from flask import Blueprint, render_template, request, jsonify
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
            mpesa_number=encrypt_contact(request.form["mpesa_number"]),
            user_name=request.form["username"],
            email=hash_email(request.form["email"]),
            password=ph.hash(request.form["password"])
        )

        try:
            db.session.add(user)
            db.session.commit()
            return "Signup successful"
        except Exception:
            db.session.rollback()
            raise

    return render_template("signup.html")

@bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_record = db.session.execute(
            db.select(User).where(
                User.email == hash_email(request.form["email"])
            )
        ).scalar()

        stored_hash = user_record.password
        password_attempt = request.form["password"]

        try:
            ph.verify(stored_hash, password_attempt)

            if ph.check_needs_rehash(stored_hash):
                updated_hash = ph.hash(password_attempt)

                try:
                    user_record.password = updated_hash
                    db.session.commit()
                except Exception:
                    db.session.rollback()
                    raise

            return "subscription's page"  # create a welcome page
                                        # list of what users can do subscriptions|transactions|profile

        except VerifyMismatchError:
            return "Invalid Password - return to login page"

    return render_template("login.html")

@bp.route("/update")
def update_details():
    return "route allows users to update their details"

@bp.route("/profile")
def user_profile():
    return"displays user profile"

@bp.route("/delete-account")
def delete():
    return "route deletes user account"