from orchestrator.extensions import db
from datetime import datetime, UTC
from orchestrator.models import Subscription, Transaction
from dateutil.relativedelta import relativedelta
from orchestrator.services import Mpesa
from orchestrator.utilities.canonicalize import standardize_contact
from orchestrator.security.encryption import decrypt_contact, decrypt_acc_number
import time
import requests
from orchestrator.utilities.activate_subscription import activate_subscription

def fetch_due_subscriptions(batch_size):
    subscriptions = db.session.execute(
        db.select(Subscription).where(
            Subscription.next_payment_at <= datetime.now()
        ).with_for_update(
            skip_locked=True).limit(batch_size)
    ).scalars().all()

    # notify the user if subscription status is paused : notification

    return subscriptions 

def generate_idempotency_key(subscription):
    return f"{subscription.id}-{subscription.next_payment_at.isoformat() if subscription.next_payment_at else 'None'}"

def create_transaction(subscription, idempotency_key):
    transaction = Transaction(
        subscription_id=subscription.id,
        indempotency_key=idempotency_key, 
        amount=subscription.amount,
        payment_type=subscription.payment_type,
        status="pending"
    )

    db.session.add(transaction)
    db.session.flush()

    return transaction

def stk_push(mpesa, retries=3, delay=10):
    
    for attempt in range(retries):
        try:
            response = mpesa.stk_push()
            return response
        except requests.exceptions.HTTPError as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

def payment_logic(subscription_object, transaction_object): 
    # add mechanism to load payments from cards
    # removes the hustle of user having to input pin
    # automatically deducts funds and makes payment

    # how can I make deductions from credit/ debit cards and make payments to automate payments?

    mpesa_number = int(standardize_contact(decrypt_contact(subscription_object.user.mpesa_number)))

    transaction_type = ""
    business_short_code = 0
    account_ref = ""

    if transaction_object.payment_type == "Till Number":
        business_short_code = int(subscription_object.till_number) 
        transaction_type = "CustomerBuyGoodsOnline"
        account_ref = f"{subscription_object.service_name}"
    
    elif transaction_object.payment_type == "Paybill": 
        transaction_type = "CustomerPayBillOnline"
        business_short_code = int(subscription_object.paybill_number)
        account_ref = decrypt_acc_number(subscription_object.account_number)

    mpesa = Mpesa(
        mpesa_contact=mpesa_number, #254743277087
        transaction_type="CustomerPayBillOnline", #transaction_type
        business_short_code=174379, #business_short_code
        amount=1,#transaction.amount
        account_ref= account_ref,
        transaction_desc=f"{subscription_object.frequency} subscription for your {subscription_object.service_name}"
        ) 
        # customize transaction description in 
        # individual block

    response = stk_push(mpesa=mpesa)

    if response.get("ResponseCode") == "0":
        transaction_object.status = "pending"
        transaction_object.checkout_request_id = response.get("CheckoutRequestID")
        db.session.commit()
    else:
        transaction_object.status = "failed"
        transaction_object.failure_reason = response.get("errorMessage")
        db.session.commit()

    return None

def process_subscription(batch_size=5):

    subscriptions = fetch_due_subscriptions(batch_size=batch_size)

    if not subscriptions:
        print(f"no pending subscriptions | {datetime.now(UTC)}")
        return

    for subscription in subscriptions:
        try:

            if subscription.status == "paused":
                activate_subscription(subscription=subscription)
                continue 

            if subscription.status != "active":
                continue  # cancelled - user permanently stopped subscription/ deleted subscription - worker should [never charge again]
                        # payment failed - billing failed multiple times: 3 retries failed, insufficient funds - worker should [stop charging, notify the user : notification]
                      # expired - subscription duration ended - worker should [stop billing]
                    # trial - user is in free trial period - worker should - [ not charge yet until trial_end_date]
                   
            print(f"processing subscription {subscription.id} - {subscription.service_name} | user {subscription.user.id}: {subscription.user.user_name}")

            idempotency_key = generate_idempotency_key(subscription=subscription)

            existing_transaction = db.session.execute(
                db.select(Transaction).where(
                    Transaction.indempotency_key == idempotency_key
                )
            ).scalar()

            if existing_transaction:

                if existing_transaction.retry_count >= subscription.max_retries:
                    print(f"max retries for {subscription.service_name} reached. skipping...")
                    continue

                existing_transaction.status = "retrying"
                existing_transaction.last_attempted_at = datetime.now()
                db.session.commit()

                continue

            else:

                novel_transaction = create_transaction(subscription=subscription, idempotency_key=idempotency_key)
                db.session.commit()

                payment_logic(subscription_object=subscription, transaction_object=novel_transaction)

        except Exception:
            db.session.rollback()
            raise

        time.sleep(30)

    failed_transactions = db.session.execute(
        db.select(Transaction).where(
            Transaction.status == "retrying",
            Transaction.retry_count < subscription.max_retries
        )
    ).scalars().all()


    for failed_transaction in failed_transactions:


        try:
            print(f"retrying transaction {failed_transaction.id} | subscription: {failed_transaction.subscription.service_name}")
            payment_logic(subscription_object=subscription,transaction_object=failed_transaction)
            time.sleep(10)

        except Exception:
            db.session.rollback()
            raise

                    
        
        
       # set to retry at different time intervals after initial failure

































   