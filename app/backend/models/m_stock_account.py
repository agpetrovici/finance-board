from app.backend.models.db import db


class StockAccount(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "m_stock_account"

    pk_stock_account = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<StockAccount {self.name}>"
