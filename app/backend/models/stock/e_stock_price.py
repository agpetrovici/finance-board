import datetime
from typing import cast

from sqlalchemy import BigInteger, DateTime, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.models.db import Base, get_session


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

    @staticmethod
    def get_prices(
        symbol: str | list[str],
        start_date: datetime.datetime | datetime.date,
        end_date: datetime.datetime | datetime.date,
    ) -> list["StockPriceDaily"]:
        with get_session() as session:
            return cast(
                list[StockPriceDaily],
                (
                    session.query(StockPriceDaily)
                    .filter(
                        StockPriceDaily.fk_symbol.in_(symbol) if isinstance(symbol, list) else StockPriceDaily.fk_symbol == symbol,
                        StockPriceDaily.date >= start_date,
                        StockPriceDaily.date <= end_date,
                    )
                    .order_by(StockPriceDaily.date.asc())
                    .all()
                ),
            )

    @classmethod
    def get_last_price(cls, symbol: str) -> "StockPriceDaily":
        with get_session() as session:
            return cast(StockPriceDaily, session.query(cls).filter(cls.fk_symbol == symbol).order_by(cls.date.desc()).first())

    def __repr__(self) -> str:
        return f"<StockPriceDaily {self.fk_symbol} {self.date} {self.close}>"
