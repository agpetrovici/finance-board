from app.backend.models.db import db


class Deposit(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "deposit"

    pk_movement = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fk_account = db.Column(db.Integer, db.ForeignKey("account.account_pk"), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False)
    interest_maturity = db.Column(db.Numeric(10, 2), nullable=False)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    interest_rate = db.Column(db.Numeric(10, 2), nullable=False)

    name = db.Column(db.String(100))
    concept = db.Column(db.String(255))
    description = db.Column(db.Text)
    bank_id = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Deposit {self.date_creation} {self.description} {self.amount}>"
