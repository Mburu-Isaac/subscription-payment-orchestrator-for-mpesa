from orchestrator.extensions import db
from orchestrator.models import Transaction

def activate_subscription(subscription):

    # add functionalities to activate subscription after pausing
    # update payment method etc
    
    associated_transaction = db.session.execute(
        db.select(Transaction).where(
            Transaction.subscription_id == subscription.id,
            Transaction.status == "fail",
            Transaction.retry_count == 3
        )
    ).scalars().first()

    try:

        associated_transaction.retry_count = 0
        subscription.status = "active"
        subscription.max_retries = 3

        db.session.commit()

        print(f"subscription status for subscription {subscription.service_name}| user {subscription.user.id}: {subscription.user.user_name} activated")

    except Exception:
        db.session.rollback()
        raise




