from app.backend.models.db import db


class Currency(db.Model):
    __tablename__ = "m_currency"

    code = db.Column(db.String(3), primary_key=True)  # e.g., "USD", "EUR"
    name = db.Column(db.String(100))  # e.g., "United States Dollar"
    symbol = db.Column(db.String(5))  # e.g., "$"
    country = db.Column(db.String(100))  # optional
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Currency {self.code}>"
