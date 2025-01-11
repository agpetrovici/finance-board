from pathlib import Path

from flask import Flask

from app.backend.config import Config
from app.backend.models.db import db
from app.backend.routes.dashboard.dashboard import bp as bp_dashboard


def create_app(config_class: Config) -> Flask:
    template_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    db.init_app(app)

    # Blueprint registration
    app.register_blueprint(bp_dashboard)

    # Create all tables
    with app.app_context():
        db.create_all()

    return app
