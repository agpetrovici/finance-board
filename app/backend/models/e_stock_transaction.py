from app.backend.models.db import db


class StockTransaction(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "e_stock_transaction"

    pk_stock_transaction = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_stock_account = db.Column(db.Integer, db.ForeignKey("m_stock_account.pk_stock_account"), nullable=False)

    order_id = db.Column(db.String(100), nullable=False)  # id stored by the broker
    execution_date = db.Column(db.DateTime, nullable=False)
    fk_isin = db.Column(db.String(12), db.ForeignKey("m_isin.pk_isin"), nullable=False)
    fk_order_type = db.Column(db.Integer, db.ForeignKey("m_order_type.pk_order_type"), nullable=False)
    fk_order_class = db.Column(db.Integer, db.ForeignKey("m_order_class.pk_order_class"), nullable=False)
    fk_reference_exchange = db.Column(db.String(3), db.ForeignKey("m_reference_exchange.pk_reference_exchange"), nullable=True)
    fk_execution_venue = db.Column(db.String(10), db.ForeignKey("m_execution_venue.pk_execution_venue"), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)

    # Broker price per share
    price_per_share_value = db.Column(db.Numeric(10, 4), nullable=False)  # Price per share in broker's currency (e.g., USD)
    price_per_share_currency = db.Column(db.String(3), nullable=False)  # Currency of the price per share (e.g., USD)
    value_broker = db.Column(db.Numeric(10, 4), nullable=False)  # Value in broker's currency (e.g., USD)
    value_broker_currency = db.Column(db.String(3), nullable=False)  # Currency of the value in broker's currency (e.g., USD)
    fx_rate = db.Column(db.Numeric(10, 4), nullable=True)  # Exchange rate applied (e.g., 1.1187 USD/EUR)

    # User value
    value_user = db.Column(db.Numeric(10, 4), nullable=False)  # Value in user's value (e.g., USD)
    value_user_currency = db.Column(db.String(3), nullable=False)  # Value in user's currency (e.g., EUR)
    cost_autofx_value = db.Column(db.Numeric(10, 2), nullable=True)
    cost_autofx_currency = db.Column(db.String(3), db.ForeignKey("m_currency.code"), nullable=True)
    external_costs_value = db.Column(db.Numeric(10, 2), nullable=True)
    external_costs_currency = db.Column(db.String(3), db.ForeignKey("m_currency.code"), nullable=True)
    total_costs_value = db.Column(db.Numeric(10, 2), nullable=True)
    total_costs_currency = db.Column(db.String(3), db.ForeignKey("m_currency.code"), nullable=True)

    # Final total charged to the user in their currency (value_user_currency + total_costs_eur)
    total_user_value = db.Column(db.Numeric(10, 2), nullable=False)
    total_user_currency = db.Column(db.String(3), db.ForeignKey("m_currency.code"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<StockTransaction {self.execution_date} {self.fk_order_type} {self.total_user_currency}>"
