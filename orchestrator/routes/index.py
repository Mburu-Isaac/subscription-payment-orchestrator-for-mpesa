# index page route
# details about the app page

from flask import Blueprint

bp = Blueprint("main", __name__)

@bp.route("/")
def index_page():
    return "Homepage"

@bp.route("/about")
def about_app():
    return "provide details about the application"