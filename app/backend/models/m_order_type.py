from app.backend.models.db import db


class OrderType(db.Model):
    __tablename__ = "m_order_type"

    pk_order_type = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<OrderType {self.name}>"
