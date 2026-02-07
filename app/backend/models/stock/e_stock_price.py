from sqlalchemy import DateTime, ForeignKey, Integer, String, Float, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockPriceDaily(Base):
    __tablename__ = "e_stock_price_daily"
    __table_args__ = (PrimaryKeyConstraint("fk_symbol", "date"),)

    fk_symbol: Mapped[str] = mapped_column(String(10), ForeignKey("e_stock_symbol.pk_symbol"), nullable=False)
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<StockPriceDaily {self.fk_isin} {self.datetime}>"
