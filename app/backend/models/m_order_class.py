from app.backend.models.db import db


class OrderClass(db.Model):
    __tablename__ = "m_order_class"

    pk_order_class = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<OrderClass {self.name}>"
