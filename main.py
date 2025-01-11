import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent))

load_dotenv()
from app.backend.config import Config  # noqa: E402
from app.backend.models.db import db  # noqa: E402
from app.backend.routes.dashboard.dashboard import bp as bp_dashboard  # noqa: E402


def create_app(config_class=Config) -> Flask:
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


if __name__ == "__main__":
    app = create_app(Config)
    app.run(port=os.getenv("FLASK_PORT"), host=os.getenv("FLASK_HOST"))
