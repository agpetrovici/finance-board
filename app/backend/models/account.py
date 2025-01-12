from app.backend.models.db import db


class Account(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "account"

    account_pk = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))
    bank_name = db.Column(db.String(100))
    account_number = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Account {self.name}>"
