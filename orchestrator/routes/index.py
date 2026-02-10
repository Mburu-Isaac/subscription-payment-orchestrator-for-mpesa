# index page route
# details about the app page

from flask import Blueprint, render_template
from flask_login import current_user

bp = Blueprint("main", __name__)

@bp.route("/")
def index_page():
    return render_template("index.html", user=current_user)

@bp.route("/about")
def about_app():
    return "provide details about the application"