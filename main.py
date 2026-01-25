from orchestrator.extensions import db
from orchestrator import create_app
from mpesa import Mpesa

app = create_app()

# with app.app_context():
#     db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

# transaction = Mpesa()
# print(transaction.token_cache())
# print(transaction.stk_push())







