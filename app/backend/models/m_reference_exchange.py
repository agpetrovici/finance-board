from app.backend.models.db import db


class ReferenceExchange(db.Model):
    __tablename__ = "m_reference_exchange"

    pk_reference_exchange = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<ReferenceExchange {self.name}>"
