from flask import Flask
from .extensions import db

def create_app():

    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    from orchestrator import models

    return app