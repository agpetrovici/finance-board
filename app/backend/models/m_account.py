from app.backend.models.db import db


class Account(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "m_fiat_account"

    account_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    currency = db.Column(db.String(10))
    description = db.Column(db.String(255))
    # Bank account identification
    bank_name = db.Column(db.String(100))
    bank_code = db.Column(db.String(8))
    branch_code = db.Column(db.String(8))
    control_digits = db.Column(db.String(10))
    account_number = db.Column(db.String(100))
    bank_id = db.Column(db.String(50))  # unique and internal identifier that the bank provides for the account
    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Account {self.name}>"
