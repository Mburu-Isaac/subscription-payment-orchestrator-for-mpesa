# add subscription CRUD logic here
# add subscription - Create
# display subscriptions - Read
# update subscription(s) - Update
# delete subscription(s) - Delete

from flask import Blueprint

bp = Blueprint("subscription",__name__)

@bp.route("/")
def create_subscription():
    return "Route creates new subscription"

@bp.route("/show")
def read_subscription():
    return "Route displays subscription(s)"

@bp.route("/update")
def update_subscription():
    return "Route updates subscription(s)"

@bp.route("/delete")
def delete_subscription():
    return "Route deletes subscriptions"