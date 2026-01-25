from flask import Blueprint, jsonify
from .extensions import db
from .models import User, Subscription
from datetime import datetime, timedelta

bp = Blueprint("main", __name__)

@bp.route("/")
def index_page():
    return "Home Page"

@bp.route("/signup")
def create_user():

    user = User(
        mpesa_number = "0706597544",
        email = "exampleemail@gmail.com",
    )

    subscription_one = Subscription(
        service_name = "Spotify Monthly Subscription",
        payment_type = "paybill",
        paybill_number = "722722",
        account_number = "1234567891011",
        amount = 169.00,
        frequency = "monthly",
        next_payment_date = datetime.utcnow() + timedelta(days=30),
        user=user
    )

    subscription_two = Subscription(
        service_name = "Gym Subscription",
        payment_type = "Till Number",
        till_number = "8888008",
        amount = 169.00,
        frequency = "monthly",
        next_payment_date = datetime.utcnow() + timedelta(days=30),
        user = user
    )

    db.session.add(user)
    db.session.add_all(
        [subscription_one, subscription_two]
    )
    db.session.commit()

    return "user successfully registered"
# obtain user info - personal details and subscription details
# store them in the database return "register new user"

@bp.route("/subscriptions")
def subscription():

    user_subscriptions = db.session.execute(
        db.select(Subscription)
    ).scalars().all()

    return jsonify(
        [
            {
                "service_name":subscriptions.service_name,
                "payment_type":subscriptions.payment_type,
                "till_number":subscriptions.till_number,
                "paybill_number": subscriptions.paybill_number,
                "account_number":subscriptions.account_number,
                "amount":subscriptions.amount,
                "frequency":subscriptions.frequency,
                "next_payment_date":subscriptions.next_payment_date,
            }
            for subscriptions in user_subscriptions
        ]
    )

@bp.route("/update")
def update_record():
    subscription_id = 1
    subscription_update = db.get_or_404(Subscription, subscription_id)
    subscription_update.service_name = "Spotify Student Subscription"
    db.session.commit()

    return "Update was successful"

@bp.route("/delete")
def delete_record():
    record_id = 2
    db.session.delete(
        db.get_or_404(Subscription, record_id)
    )
    db.session.commit()

    return f"Record {record_id} was deleted"

@bp.route("/transactions")
def transaction():
    return "transactions"
