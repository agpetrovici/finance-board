from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class ExecutionVenue(Base):
    __tablename__ = "m_execution_venue"

    pk_execution_venue: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<ExecutionVenue {self.name}>"
