from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from orchestrator.models import Subscription, User, Transaction
from orchestrator.extensions import db
from datetime import datetime
from orchestrator.security.encryption import (
    encrypt_acc_number,
    decrypt_acc_number,
    decrypt_contact,
)
from orchestrator.utilities.slugify_utils import slugify_object
from orchestrator.security.hashing import generate_subscription_fingerprint
from orchestrator.utilities.validate_subscription import subscription_validation
from pprint import pprint


bp = Blueprint("subscription", __name__)


@bp.route("/")
@login_required
def subscription_index():
    # add a link - create subscription - that redirects to create_subscription route
    user = db.session.execute(db.select(User)).scalar()

    subscription_records = user.subscriptions

    return render_template(
        "subscriptions.html",
        subscriptions=subscription_records,
    )


@bp.route("/add-subscription", methods=["POST", "GET"])
@login_required
def create_subscription():

    # set constraint that till numbers should be unique per service

    if request.method == "POST":

        form_data = request.form.to_dict()

        service_name = form_data.get("service_name")
        next_payment_str = form_data.get("next_payment_date")
        payment_type = form_data.get("payment_type")
        till_number = form_data.get("till_number")
        paybill_number = form_data.get("paybill_number")
        account_number = form_data.get("account_number")
        amount = form_data.get("amount")
        frequency = form_data.get("frequency")

        error = subscription_validation(
            service_name=service_name,
            next_payment_str=next_payment_str,
            payment_type=payment_type,
            till_number=till_number,
            paybill_number=paybill_number,
            account_number=account_number,
            amount=amount,
            frequency=frequency,
            form_data=form_data
        )

        if error:
            flash(error, "info")
            return render_template(
                "subscription-actions.html",
                form_data=form_data
            )

        fingerprint = generate_subscription_fingerprint(
                user_id=current_user.id,
                service_name=service_name,
                payment_type=payment_type,
                account_number=account_number,
                paybill_number=paybill_number,
                till_number=till_number
            )

        subscription = db.session.execute(
            db.select(
                Subscription).where(Subscription.fingerprint == fingerprint)
                ).scalars().all()

        if subscription:
            flash("subscription already exists", "info")
            return render_template(
                "subscription-actions.html",
                form_data=form_data
            )
        
        else:

            slug = slugify_object(service_name)
            next_payment_date = datetime.strptime(next_payment_str, "%Y-%m-%d").date()
            account_number = encrypt_acc_number(account_number) if account_number else None

            subscription = Subscription(
                service_name=service_name,
                slug=slug,
                payment_type=payment_type,
                till_number=till_number or None,
                paybill_number=paybill_number or None,
                account_number=account_number or None,
                amount=amount,
                frequency=frequency,
                next_payment_date=next_payment_date,
                next_payment_at=next_payment_date,
                user=current_user,
                fingerprint=fingerprint,
            )

            try:
                db.session.add(subscription)
                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

            return redirect(
                url_for("subscription.create_subscription")
            ) 

    return render_template(
        "subscription-actions.html",
        subscription=None,
        form_data={}
    )


@bp.route("/show/<slug>")
@login_required
def read_subscription(slug):
    subscription = db.session.execute(
        db.select(Subscription).where(Subscription.slug == slug)
    ).scalar()

    mpesa_number = decrypt_contact(subscription.user.mpesa_number)

    if not subscription.account_number: 
        account_number = None
    elif subscription.account_number:
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
        )
    ).scalar()

    if request.method == "POST":

        form_data = request.form.to_dict()

        service_name = form_data.get("service_name")
        next_payment_str = form_data.get("next_payment_date")
        payment_type = form_data.get("payment_type")
        till_number = form_data.get("till_number")
        paybill_number = form_data.get("paybill_number")
        account_number = form_data.get("account_number")
        amount = form_data.get("amount")
        frequency = form_data.get("frequency")
            

        error = subscription_validation(
            service_name=service_name,
            next_payment_str=next_payment_str,
            payment_type=payment_type,
            till_number=till_number,
            paybill_number=paybill_number,
            account_number=account_number,
            amount=amount,
            frequency=frequency,
            form_data=form_data
        )

        if error:
            flash(error, "info")
            return render_template(
                "subscription-actions.html",
                form_data=form_data
            )

        account_number = encrypt_acc_number(account_number) if account_number else None

        fingerprint = generate_subscription_fingerprint(
            user_id=current_user.id,
            service_name=service_name,
            payment_type=payment_type,
            account_number=account_number,
            paybill_number=paybill_number,
            till_number=till_number
        )

        change_true = {}

        slug = None

        record_fields = [
            column.name
            for column in Subscription.__table__.columns
            if not column.primary_key
            and column.name not in ["created_at", "status", "user_id"]
        ]


        for field in record_fields:
            updated_value = form_data.get(field)
            initial_value = getattr(subscription, field)

            if field == "account_number" and initial_value:
                initial_value = decrypt_acc_number(initial_value)
            elif field == "next_payment_date" and updated_value:
                updated_value = datetime.strptime(updated_value, "%Y-%m-%d")

            if field == "account_number" and updated_value:
                updated_value = encrypt_acc_number(updated_value)

            if field == "service_name" and updated_value:
                slug = slugify_object(updated_value)

            if field == "next_payment_date" and updated_value:
                subscription.next_payment_date = updated_value

            if field == "max_retries":
                if updated_value is not None and updated_value != "":
                    updated_value = int(updated_value)
                else:
                    updated_value = getattr(subscription, field)

            if updated_value != initial_value:
                setattr(subscription, field, updated_value)
                change_true[field] = updated_value                

        if change_true:

            try:
                if slug:
                    subscription.slug = slug

                if subscription.payment_type == "Till Number":
                    subscription.account_number = None

                subscription.fingerprint = fingerprint

                db.session.commit()
            except Exception:
                db.session.rollback()
                raise

        return redirect(
            url_for(
                "subscription.read_subscription",  # provide feedback to user - update successful|update failed : notification
                slug=subscription.slug,
            )
        )

    mpesa_number = decrypt_contact(subscription.user.mpesa_number)

    if not subscription.account_number:
        account_number = None
    elif subscription.account_number:
        account_number = decrypt_acc_number(subscription.account_number)

    if not subscription:
            print(f"subscription {subscription.id} : {subscription.service_name} not found | user {subscription.user.user_id}")  


    form_data = {
        column.name: getattr(subscription, column.name)
        for column in subscription.__table__.columns
        if not column.primary_key
    }

    form_data["account_number"] = account_number or ""
    form_data["mpesa_number"] = mpesa_number or ""


    if form_data.get("next_payment_date"): # find a way to display already input date by user in html template
        # form_data["next_payment_date"] = form_data.get("next_payment_date")
        pass
    elif subscription and subscription.next_payment_date:
        form_data["next_payment_date"] = subscription.next_payment_date.strftime("%Y-%m-%d")
    else:
        form_data["next_payment_date"] = ""

    return render_template(
        "subscription-actions.html",
        subscription=subscription,
        form_data=form_data,
    )


@bp.route("/delete/<slug>") 
@login_required
def delete_subscription(slug):

    subscription_record = db.session.execute(
        db.select(Subscription).where(Subscription.slug == slug)
    ).scalar()

    if not subscription_record:
        return "record cannot be found" # mechanism to handle when deletion on an already deleted record : defensive

    try:

        # Add confirmation that the user wants to delete the record

        db.session.delete(
            subscription_record
        )  
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    flash("record was deleted successfully")
    return redirect(
        url_for("subscription.subscription_index")
    )  
