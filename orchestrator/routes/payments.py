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