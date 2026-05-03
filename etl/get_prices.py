import datetime

from sqlalchemy.dialects.postgresql import insert

from app.integrations.twelve_data.stock_api import IntervalTwelveData, StockApi
from app.backend.models.db import get_session
from app.backend.models.stock.e_stock_price import StockPriceDaily


def get_prices(
    symbol: str,
    start_date: datetime.datetime | datetime.date,
    end_date: datetime.datetime | datetime.date,
    interval: IntervalTwelveData = IntervalTwelveData.DAILY,
    timezone: str = "UTC",
) -> None:

    if isinstance(start_date, datetime.date):
        start_date_adj = datetime.datetime(year=start_date.year, month=start_date.month, day=start_date.day)
    else:
        start_date_adj = start_date
    if isinstance(end_date, datetime.date):
        end_date_adj = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    else:
        end_date_adj = end_date

    stock_api = StockApi()
    prices = stock_api.get_prices(
        symbol,
        interval,
        start_date=start_date_adj,
        end_date=end_date_adj,
        timezone=timezone,
    )

    if not prices:
        return

    rows = [
        {
            "fk_symbol": p.fk_symbol,
            "date": p.date,
            "open": p.open,
            "high": p.high,
            "low": p.low,
            "close": p.close,
            "volume": p.volume,
        }
        for p in prices
    ]

    stmt = insert(StockPriceDaily).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["fk_symbol", "date"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
        },
    )

    with get_session() as session:
        session.execute(stmt)
        session.commit()
