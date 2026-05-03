from datetime import datetime
from typing import cast

from sqlalchemy import BigInteger, DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base, get_session


class StockPrice15min(Base):
    __tablename__ = "e_stock_price_15min"
    __table_args__ = (PrimaryKeyConstraint("fk_symbol", "datetime"),)

    fk_symbol: Mapped[str] = mapped_column(String(10), ForeignKey("e_stock_symbol.pk_symbol"))
    datetime: Mapped[datetime] = mapped_column("datetime", DateTime)

    open: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    close: Mapped[float]

    volume: Mapped[int] = mapped_column(BigInteger)

    @staticmethod
    def get_prices(
        symbol: str | list[str],
        start: datetime,
        end: datetime,
    ) -> list["StockPrice15min"]:
        with get_session() as session:
            return cast(
                list[StockPrice15min],
                (
                    session.query(StockPrice15min)
                    .filter(
                        StockPrice15min.fk_symbol.in_(symbol) if isinstance(symbol, list) else StockPrice15min.fk_symbol == symbol,
                        StockPrice15min.datetime >= start,
                        StockPrice15min.datetime <= end,
                    )
                    .order_by(StockPrice15min.datetime.asc())
                    .all()
                ),
            )

    @classmethod
    def get_last_price(cls, symbol: str) -> datetime:
        with get_session() as session:
            return session.query(cls).filter(cls.fk_symbol == symbol).order_by(cls.datetime.desc()).first()

    def __repr__(self) -> str:
        return f"<StockPrice15min {self.fk_symbol} {self.datetime} {self.close}>"
