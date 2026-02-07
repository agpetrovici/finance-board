from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class Currency(Base):
    __tablename__ = "m_currency"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)  # e.g., "USD", "EUR"
    name: Mapped[str | None] = mapped_column(String(100))  # e.g., "United States Dollar"
    symbol: Mapped[str | None] = mapped_column(String(5))  # e.g., "$"
    country: Mapped[str | None] = mapped_column(String(100))  # optional
    is_active: Mapped[bool | None] = mapped_column(Boolean, default=True)

    def __repr__(self) -> str:
        return f"<Currency {self.code}>"
