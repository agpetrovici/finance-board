import datetime

from sqlalchemy.dialects.postgresql import insert

from app.integrations.twelve_data.stock_api import IntervalTwelveData, StockApi
from app.backend.models.db import get_session
from app.backend.models.e_fx_rate import FxRateDaily


def get_fx_rates(
    pair: str,
    start_date: datetime.datetime | datetime.date,
    end_date: datetime.datetime | datetime.date,
    interval: IntervalTwelveData = IntervalTwelveData.DAILY,
    timezone: str = "UTC",
) -> None:

    if isinstance(start_date, datetime.date) and not isinstance(start_date, datetime.datetime):
        start_date_adj = datetime.datetime(year=start_date.year, month=start_date.month, day=start_date.day)
    else:
        start_date_adj = start_date
    if isinstance(end_date, datetime.date) and not isinstance(end_date, datetime.datetime):
        end_date_adj = datetime.datetime(year=end_date.year, month=end_date.month, day=end_date.day)
    else:
        end_date_adj = end_date

    stock_api = StockApi()
    rates = stock_api.get_fx_prices(
        pair,
        interval,
        start_date=start_date_adj,
        end_date=end_date_adj,
        timezone=timezone,
    )

    if not rates:
        return

    rows = [
        {
            "currency_pair": r.currency_pair,
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
        }
        for r in rates
    ]

    stmt = insert(FxRateDaily).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["currency_pair", "date"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
        },
    )

    with get_session() as session:
        session.execute(stmt)
        session.commit()
