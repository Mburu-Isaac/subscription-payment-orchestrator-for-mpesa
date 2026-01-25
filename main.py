from orchestrator.extensions import db
from orchestrator import create_app
from mpesa import Mpesa

app = create_app()

# with app.app_context():
#     db.create_all()

# transaction = Mpesa()
# print(transaction.token_cache())
# print(transaction.stk_push())







