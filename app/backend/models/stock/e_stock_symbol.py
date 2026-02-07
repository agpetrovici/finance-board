from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockSymbol(Base):
    __tablename__ = "e_stock_symbol"

    pk_symbol: Mapped[str] = mapped_column(String(10), primary_key=True)
    fk_isin: Mapped[str] = mapped_column(String(12), ForeignKey("m_isin.pk_isin"), nullable=False)

    def __repr__(self) -> str:
        return f"<StockSymbol {self.pk_symbol}>"
