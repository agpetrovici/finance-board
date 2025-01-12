from pathlib import Path

from flask import Flask

from app.backend.config import Config
from app.backend.models.db import db
from app.backend.routes.dashboard.dashboard import bp as bp_dashboard
from app.backend.routes.api.api import bp as bp_api


def create_app(config_class: type[Config] = Config) -> Flask:
    template_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    db.init_app(app)

    # Blueprint registration
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_api)

    # Create all tables
    with app.app_context():
        from app.backend.models.account import Account  # noqa: F401
        from app.backend.models.transaction import Transaction  # noqa: F401

        db.create_all()

    return app
