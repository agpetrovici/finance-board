from app.backend.models.db import db


class AccountCrypto(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "m_crypto_account"

    pk_account_crypto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    exchange = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<AccountCrypto {self.name}>"
