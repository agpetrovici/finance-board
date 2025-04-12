from app.backend.models.db import db


class StockPortfolio(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "e_stock_portfolio"

    pk_stock_portfolio = db.Column(db.Integer, primary_key=True, autoincrement=True)

    fk_stock_account = db.Column(db.Integer, db.ForeignKey("m_stock_account.pk_stock_account"), nullable=False)
    fk_isin = db.Column(db.String(12), db.ForeignKey("m_isin.pk_isin"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<StockPortfolio {self.execution_date} {self.fk_order_type} {self.total_user_currency}>"
