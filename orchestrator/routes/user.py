from flask_login import login_required
from flask import Blueprint

bp = Blueprint("user", __name__)

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