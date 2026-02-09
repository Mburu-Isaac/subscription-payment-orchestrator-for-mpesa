# add "add new subscription" button to create subscription form
# clear fields when user wants to add a new record

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from orchestrator.models import Subscription, User
from orchestrator.extensions import db
from datetime import datetime
from orchestrator.security.encryption import (
    encrypt_acc_number,
    decrypt_acc_number,
    decrypt_contact,
)
from orchestrator.utilities.slugify_utils import slugify_object


bp = Blueprint("subscription", __name__)


@bp.route("/")
@login_required
def subscription_index():
    # link to the home page - able to return to the dashboard and accessed from the dashboard
    # add button to add to the subscriptions - links to the create_subscription route
    user = db.session.execute(db.select(User)).scalar()

    subscription_records = user.subscriptions

    return render_template(
        "subscriptions.html",
        subscriptions=subscription_records,
    )


@bp.route("/add-subscription", methods=["POST", "GET"])
@login_required
def create_subscription():
    # make the next payment automatically recur - after 30/365/366 days -
    # after the user indicates the next payment while creating the subscription
    if request.method == "POST":

        next_payment_str = request.form.get("next_payment_date")
        next_payment_date = datetime.strptime(next_payment_str, "%Y-%m-%d").date()
        service_name = service_name = request.form.get("service_name")
        slug = slugify_object(service_name)

        subscription = Subscription(
            service_name=service_name,
            slug=slug,
            payment_type=request.form.get("payment_type"),
            till_number=request.form.get("till_number") or None,
            paybill_number=request.form.get("paybill_number") or None,
            account_number=encrypt_acc_number(request.form.get("account_number"))
            or None,
            amount=request.form.get("amount"),
            frequency=request.form.get("frequency"),
            next_payment_date=next_payment_date,
            user=current_user,
        )

        try:
            db.session.add(subscription)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return redirect(
            url_for("subscription.subscription_index")
        )  # implement a button allowing users to add subscription records
    return render_template("subscription-actions.html", subscription=None)


@bp.route("/show/<slug>")
@login_required
def read_subscription(slug):
    subscription = db.session.execute(
        db.select(Subscription).where(Subscription.slug == slug)
    ).scalar()

    mpesa_number = decrypt_contact(subscription.user.mpesa_number)
    account_number = decrypt_acc_number(subscription.account_number)

    if not subscription:
        return "Subscription cannot be found"

    return render_template(
        "subscription-details.html",
        subscription=subscription,
        mpesa_number=mpesa_number,
        account_number=account_number,
    )


@bp.route("/update/<slug>", methods=["POST", "GET"])
@login_required
def update_subscription(slug):

    subscription = db.session.execute(
        db.select(Subscription).where(
            Subscription.slug == slug
        )  # NoneType - slug not being rendered
    ).scalar()

    print(subscription)

    if request.method == "POST":
        change_true = {}

        slug = request.form.get("slug")
        # print(slug)

        record_fields = [
            column.name
            for column in Subscription.__table__.columns
            if not column.primary_key
            and column.name not in ["created_at", "status", "user_id"]
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

            if field == "service_name" and updated_value:
                slug = slugify_object(updated_value)
                # print(slug)

            if updated_value != initial_value:
                setattr(subscription, field, updated_value)
                change_true[field] = updated_value


        if change_true or slug:

            try:
                subscription.slug = slug
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return redirect(
            url_for(
                "subscription.read_subscription",  # provide feedback to user - update successful|update failed
                slug=subscription.slug,
            )
        )

    mpesa_number = decrypt_contact(subscription.user.mpesa_number)
    account_number = decrypt_acc_number(subscription.account_number)

    if not subscription:
        return (
            "subscription not found"  # add action when record is not found - a redirect
        )

    return render_template(
        "subscription-actions.html",
        subscription=subscription,
        mpesa_number=mpesa_number,
        account_number=account_number,
    )


@bp.route("/delete/<slug>")  # implement slug in place of subscription ID
@login_required
def delete_subscription(slug):
    subscription_record = db.session.execute(
        db.select(Subscription).where(Subscription.slug == slug)
    ).scalar()

    if not subscription_record:
        return "record cannot be found"

    try:
        db.session.delete(
            subscription_record
        )  # Add confirmation that the user wants to delete the record
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    flash("record was deleted successfully")
    return redirect(
        url_for("subscription.subscription_index")
    )  # notify user on record deletion - successful|unsuccessful
