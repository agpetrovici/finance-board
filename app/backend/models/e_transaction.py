from app.backend.models.db import db


class Transaction(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "e_fiat_transaction"

    transaction_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    account_fk = db.Column(db.Integer, db.ForeignKey("m_fiat_account.account_pk"), nullable=False)
    label = db.Column(db.String(100))
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))

    name = db.Column(db.String(100))
    concept = db.Column(db.String(255))
    description = db.Column(db.Text)
    bank_id = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Transaction {self.date} {self.description} {self.amount}>"
