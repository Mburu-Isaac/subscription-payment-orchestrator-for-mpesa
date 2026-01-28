# handle payment functions
# catch mpesa CallBackUrl
# add to transaction table

from flask import Blueprint,request,jsonify
from orchestrator.services import Mpesa
from orchestrator.models import Transaction
from orchestrator.extensions import db
from pprint import pprint

bp = Blueprint("payment", __name__)
mpesa = Mpesa()

@bp.route("/make-payment")
def make_payment():
    mpesa.token_cache()
    return mpesa.stk_push()

@bp.route("/stk-callback", methods=["POST", "GET"])
def stk_callback():
    callback_data = request.get_json(silent=True)

    if not callback_data:
        return {
            "error":"invalid json"
        }, 400

    pprint(callback_data)

    callback = callback_data['Body']['stkCallback']
    result_code = callback['ResultCode']
    checkout_request_id = callback['CheckoutRequestID']
    result_description = callback['ResultDesc']

    if result_code == 0:
        amount = float(callback['CallbackMetadata']['Item'][0]['Value'])
        receipt_number = callback['CallbackMetadata']['Item'][1]['Value']

        transaction = Transaction(
            amount=amount,
            payment_type="PaybillOnline",
            status="Success",
            checkout_request_id=checkout_request_id,
            mpesa_receipt_number=receipt_number,
            subscription_id=1
        )

        db.session.add(transaction)
        db.session.commit()

    else:
        transaction = Transaction(
            payment_type="PaybillOnline",
            amount=1.0,
            status="Fail",
            checkout_request_id=checkout_request_id,
            subscription_id=1,
            failure_reason=result_description
        )

        db.session.add(transaction)
        db.session.commit()

    return jsonify(
        {
            "ResultCode":0,
            "ResultDesc":"success"
        }
    )

@bp.route("/view-transactions")
def view_transactions():
    transactions = db.session.execute(
        db.select(Transaction)
    ).scalars().all()

    return jsonify(
        [
            {
                "id":transaction.id,
                "subscription_id":transaction.subscription_id,
                "amount":transaction.amount,
                "payment_type":transaction.payment_type,
                "status":transaction.status,
                "checkout_request_id":transaction.checkout_request_id,
                "mpesa_receipt_number":transaction.mpesa_receipt_number,
                "failure_reason":transaction.failure_reason,
                "created_at":transaction.created_at
            }
         for transaction in transactions
         ]
    )