from pathlib import Path

from flask import Flask, redirect, url_for
from werkzeug.wrappers.response import Response

from app.backend.config import Config
from app.backend.models.db import db
from app.backend.routes.api.api import bp as bp_api
from app.backend.routes.dashboard.dashboard import bp as bp_dashboard
from app.backend.routes.imports.imports import bp as bp_imports


def create_app(config_class: type[Config] = Config) -> Flask:
    template_dir = Path(__file__).parent / "templates"
    static_dir = Path(__file__).parent / "static"
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(bp_api)
    app.register_blueprint(bp_dashboard)
    app.register_blueprint(bp_imports)

    # Create all tables
    with app.app_context():
        from app.backend.models.m_account import Account  # noqa: F401
        from app.backend.models.m_account_crypto import AccountCrypto  # noqa: F401
        from app.backend.models.m_currency import Currency  # noqa: F401
        from app.backend.models.m_execution_venue import ExecutionVenue  # noqa: F401
        from app.backend.models.m_isin import Isin  # noqa: F401
        from app.backend.models.m_order_class import OrderClass  # noqa: F401
        from app.backend.models.m_order_type import OrderType  # noqa: F401
        from app.backend.models.m_reference_exchange import ReferenceExchange  # noqa: F401
        from app.backend.models.m_stock_account import StockAccount  # noqa: F401
        from app.backend.models.e_balance_crypto import BalanceCrypto  # noqa: F401
        from app.backend.models.e_deposit import Deposit  # noqa: F401
        from app.backend.models.e_stock_portfolio import StockPortfolio  # noqa: F401
        from app.backend.models.e_stock_transaction import StockTransaction  # noqa: F401
        from app.backend.models.e_transaction import FiatTransaction  # noqa: F401

        db.create_all()

    @app.route("/")
    def index() -> Response:
        return redirect(url_for("dashboard.get_dashboard"))

    return app
