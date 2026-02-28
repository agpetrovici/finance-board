import datetime
from typing import Optional, cast

from sqlalchemy import DateTime, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from sqlalchemy.orm import Session

class FxRateDaily(Base):
    __tablename__ = "e_fx_rate_daily"
    __table_args__ = (PrimaryKeyConstraint("currency_pair", "date"),)

    currency_pair: Mapped[str] = mapped_column(String(10))
    date: Mapped[datetime.datetime] = mapped_column(DateTime)

    open: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    close: Mapped[float]

    @staticmethod
    def get_rates(
        pair: str,
        start_date: datetime.datetime | datetime.date,
        end_date: datetime.datetime | datetime.date,
        session: Session,
    ) -> list["FxRateDaily"]:
        return cast(
            list[FxRateDaily],
            (
                session.query(FxRateDaily)
                .filter(
                    FxRateDaily.currency_pair == pair,
                    FxRateDaily.date >= start_date,
                    FxRateDaily.date <= end_date,
                )
                .order_by(FxRateDaily.date.asc())
                .all()
            ),
        )

    @classmethod
    def get_last_rate(cls, pair: str, session: Session) -> Optional["FxRateDaily"]:
        return session.query(cls).filter(cls.currency_pair == pair).order_by(cls.date.desc()).first()

    def __repr__(self) -> str:
        return f"<FxRateDaily {self.currency_pair} {self.date} {self.close}>"
