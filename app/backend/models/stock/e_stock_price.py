import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base


class StockPriceDaily(Base):
    __tablename__ = "e_stock_price_daily"
    __table_args__ = (PrimaryKeyConstraint("fk_symbol", "date"),)

    fk_symbol: Mapped[str] = mapped_column(String(10), ForeignKey("e_stock_symbol.pk_symbol"))
    date: Mapped[datetime.datetime] = mapped_column(DateTime)

    open: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    close: Mapped[float]

    volume: Mapped[int] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"<StockPriceDaily {self.fk_symbol} {self.date} {self.close}>"
