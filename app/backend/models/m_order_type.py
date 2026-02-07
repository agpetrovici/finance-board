from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class OrderType(Base):
    __tablename__ = "m_order_type"

    pk_order_type: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<OrderType {self.name}>"
