from app.backend.models.db import db


class Client(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "m_client"

    pk_client = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        return f"<Client {self.name}>"
