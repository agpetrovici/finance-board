from app.backend.models.db import db


class ExecutionVenue(db.Model):  # type: ignore[name-defined, misc]
    __tablename__ = "m_execution_venue"

    pk_execution_venue = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"<ExecutionVenue {self.name}>"
