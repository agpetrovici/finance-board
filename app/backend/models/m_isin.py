from app.backend.models.db import db


class Isin(db.Model):
    __tablename__ = "m_isin"

    pk_isin = db.Column(db.String(12), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<Isin {self.name}>"
