from app.backend.models.db import db


class BalanceCrypto(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "balance_crypto"

    fk_account_crypto = db.Column(db.Integer, db.ForeignKey("account_crypto.pk_account_crypto"), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    asset = db.Column(db.String(100), nullable=False)

    free = db.Column(db.Numeric(10, 2), nullable=False)
    locked = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (db.PrimaryKeyConstraint(fk_account_crypto, timestamp, asset),)

    def __repr__(self) -> str:
        return f"<Deposit {self.date_creation} {self.description} {self.amount}>"
