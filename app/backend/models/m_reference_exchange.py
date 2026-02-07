from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class ReferenceExchange(Base):
    __tablename__ = "m_reference_exchange"

    pk_reference_exchange: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<ReferenceExchange {self.name}>"
