from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class Isin(Base):
    __tablename__ = "m_isin"

    pk_isin: Mapped[str] = mapped_column(String(12), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<Isin {self.name}>"
