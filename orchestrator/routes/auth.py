# Handle user creation - signup
# Handle user authentication - login

from flask import Blueprint

bp = Blueprint("user", __name__)

@bp.route("/signup")
def signup():
    return "sign in new user"

@bp.route("/login")
def login():
    return "user log in"

@bp.route("/update")
def update_details():
    return "route allows users to update their details"

@bp.route("/profile")
def user_profile():
    return"displays user profile"

@bp.route("/delete-account")
def delete():
    return "route deletes user account"