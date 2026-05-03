import datetime
from typing import cast

from sqlalchemy import Table

from etl.fx.get_fx_rates import get_fx_rates
from app.backend.models.db import Base, engine, get_session
from app.backend.models.e_fx_rate import FxRateDaily

PAIR = "EUR/USD"
DEFAULT_START = datetime.date(2020, 1, 1)

if __name__ == "__main__":
    Base.metadata.create_all(engine, tables=[cast(Table, FxRateDaily.__table__)])

    with get_session() as session:
        last_rate = FxRateDaily.get_last_rate(PAIR, session)
    start_date = last_rate.date.date() if last_rate else DEFAULT_START
    end_date = datetime.datetime.now().date()

    print(f"Fetching {PAIR} from {start_date} to {end_date}")
    get_fx_rates(PAIR, start_date, end_date)
    print("done")
