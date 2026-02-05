from flask import Flask
from .extensions import db, login_manager

def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    from orchestrator import models

    from orchestrator.routes.payments import bp as transactions_bp
    from orchestrator.routes.subscriptions import bp as subscriptions_bp
    from orchestrator.routes.auth import bp as auth_bp
    from orchestrator.routes.index import bp as index_bp
    from orchestrator.routes.user import bp as user_bp

    app.register_blueprint(transactions_bp, url_prefix="/transactions")
    app.register_blueprint(subscriptions_bp, url_prefix="/subscriptions")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(index_bp)

    return app