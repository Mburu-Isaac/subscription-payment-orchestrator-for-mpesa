from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from orchestrator.models import Subscription
from orchestrator.extensions import db
from datetime import datetime
from orchestrator.security.encryption import encrypt_acc_number, decrypt_acc_number, decrypt_contact

bp = Blueprint("subscription",__name__)

@bp.route("/")
@login_required
def subscription_index():
    # link to the dashboard - able to return to the dashboard and accessed from the dashboard
    # add button to add to the subscriptions - links to the create_subscription route
    user_subscription_records = db.session.execute(
        db.select(Subscription).where(
            Subscription.user_id == current_user.id
        )
    ).scalars().all()
    return render_template("subscriptions.html", subscriptions=user_subscription_records)

@bp.route("/add-subscription", methods=["POST","GET"])
@login_required
def create_subscription():
    # make the next payment automatically recur - after 30/365/366 days -
    # after the user indicates the next payment while creating the subscription
    if request.method == "POST":

        next_payment_str = request.form.get("next_payment_date")
        next_payment_date = datetime.strptime(next_payment_str, "%Y-%m-%d").date()

        subscription = Subscription(
            service_name=request.form.get("service_name"),
            payment_type=request.form.get("payment_type"),
            till_number=request.form.get("till_number") or None,
            paybill_number=request.form.get("paybill_number") or None,
            account_number=encrypt_acc_number(request.form.get("account_number")) or None,
            amount=request.form.get("amount"),
            frequency=request.form.get("frequency"),
            next_payment_date=next_payment_date,
            user=current_user
        )

        try:
            db.session.add(subscription)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return redirect(url_for("subscription.subscription_index")) # implement a button allowing users to add subscription records
    return render_template("subscription-actions.html", subscription=None)

@bp.route("/show/<int:subscription_id>")
@login_required
def read_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)
    mpesa_number = decrypt_contact(subscription.user.mpesa_number)
    account_number = decrypt_acc_number(subscription.account_number)

    if not subscription:
        return "Subscription cannot be found"

    return render_template(
        "subscription-details.html",
        details=subscription,
        mpesa_number=mpesa_number,
        account_number=account_number
    )

@bp.route("/update/<int:subscription_id>", methods=["POST", "GET"])
@login_required
def update_subscription(subscription_id):
    # update logic
    if request.method == "POST":
        change_true = {}

        subscription = db.session.get(Subscription, subscription_id)

        record_fields = [
            column.name for column in Subscription.__table__.columns
            if not column.primary_key and column.name not in ["created_at", "status", "user_id"]
        ]

        for field in record_fields:
            updated_value = request.form.get(field)
            initial_value = getattr(subscription, field)

            if field == "account_number" and initial_value:
                initial_value = decrypt_acc_number(initial_value)
            elif field == "next_payment_date" and updated_value:
                updated_value = datetime.strptime(updated_value, "%Y-%m-%d")

            if field == "account_number" and updated_value:
                updated_value = encrypt_acc_number(updated_value)


            if updated_value != initial_value:
                setattr(subscription, field, updated_value)
                change_true[field] = updated_value

        if change_true:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return redirect(
            url_for(
                "subscription.read_subscription", # provide feedback to user - update successful|update failed
                subscription_id=subscription_id
            )
        )

    subscription = db.session.get(Subscription, subscription_id)
    mpesa_number = decrypt_contact(subscription.user.mpesa_number)
    account_number = decrypt_acc_number(subscription.account_number)

    if not subscription:
        return "subscription not found" # add action when record is not found - a redirect

    return render_template(
        "subscription-actions.html",
        subscription=subscription,
        mpesa_number=mpesa_number,
        account_number=account_number
    )

@bp.route("/delete/<int:subscription_id>")
@login_required
def delete_subscription(subscription_id):
    subscription_record = db.session.get(Subscription, subscription_id)

    if not subscription_record:
        return "record cannot be found"

    try:
        db.session.delete(subscription_record)  #Add confirmation that the user wants to delete the record
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return redirect(url_for("subscription.subscription_index")) # notify user on record deletion - successful|unsuccessful



