from flask import Blueprint,request,jsonify
from orchestrator.models import Transaction, Subscription
from orchestrator.extensions import db
# from datetime import datetime,time,timedelta,date
from orchestrator.utilities.recur import recur

bp = Blueprint("payment", __name__)


@bp.route("/stk-callback", methods=["POST", "GET"])
def stk_callback():
    data = request.get_json(silent=True)

    if not data:
        return {
            "error":"invalid json"
        }, 400

    # pprint(data)

    if (callback_data := data.get("Body", {}).get("stkCallback")):
        result_code = callback_data.get("ResultCode")
        checkout_request_id = callback_data.get("CheckoutRequestID")
        result_desc = callback_data.get("ResultDesc")

        transaction = db.session.execute(
            db.select(Transaction).where(
                Transaction.checkout_request_id == checkout_request_id
            )
        ).scalar()

        subscription = db.session.get(Subscription,transaction.subscription.id)
    
        try:

            if result_code == 0:

                callback_metadata_item = callback_data.get("CallbackMetadata").get("Item")
                mpesa_receipt_number = callback_metadata_item[1].get("Value")

                transaction.status = "success"
                transaction.checkout_request_id = checkout_request_id
                transaction.mpesa_receipt_number = mpesa_receipt_number

                subscription.next_payment_at = recur(
                    base_date = subscription.next_payment_date,
                    frequency = subscription.frequency
                )

                transaction.retry_count = 0

            else:
                transaction.status = "fail"
                transaction.failure_reason = result_desc

                transaction.retry_count += 1

                if subscription.max_retries is None:
                    subscription.max_retries = 3

                if transaction.retry_count >= subscription.max_retries:
                    subscription.status = "paused"  
                    print(f"{subscription.service_name} paused") # notify the user when subcription is paused : notification
            
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
    else:
        ResultCode = CheckoutRequest_id = ResultDesc = None


    return jsonify(
        {
            "ResultCode":0,
            "ResultDesc":"success"
        }
    )

@bp.route("/view-transactions")
def view_transactions():
    pass



