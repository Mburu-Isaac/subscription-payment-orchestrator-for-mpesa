# handle payment functions
# add to transaction table

from flask import Blueprint,request,jsonify
from orchestrator.services import Mpesa
from orchestrator.models import Transaction, Subscription
from orchestrator.extensions import db
from pprint import pprint
from orchestrator.security.encryption import decrypt_contact, decrypt_acc_number
from orchestrator.utilities.canonicalize import standardize_contact

bp = Blueprint("payment", __name__)

@bp.route("/make-payment/<int:subscription_id>")
def make_payment(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)

    mpesa_contact = int(
        standardize_contact(
            decrypt_contact(
                subscription.user.mpesa_number
            )
        )
    )

    transaction_type = ""
    business_short_code = 0

    if subscription.payment_type == "Till Number":
        business_short_code = int(subscription.till_number) # "174379"
        transaction_type = "CustomerBuyGoodsOnline"
    elif subscription.payment_type == "Paybill": # check if C2B allows payments to banks using paybill
        transaction_type = "CustomerPaybillOnline"
        # assess making payments to banks
        pass
        # account reference = decrypt_acc_number(subscription.account_number)

    mpesa = Mpesa(
        mpesa_contact=mpesa_contact,
        transaction_type=transaction_type,
        business_short_code=business_short_code,
        amount=int(subscription.amount),
        account_ref=subscription.service_name,
        transaction_desc=f"{subscription.frequency} subscription for your {subscription.service_name}"
    )

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


        # use relationship to specify transaction type - subscription.payment_type
        # use relationship to specify subscription id


    return jsonify(
        {
            "ResultCode":0,
            "ResultDesc":"success"
        }
    )

@bp.route("/view-transactions")
def view_transactions():
    pass



# make payment - do when implementing automation mechanism