import os
from typing import Sequence
import datetime
from typing import Optional
from pydantic import BaseModel
from twelvedata import TDClient
from enum import Enum

from app.backend.models.stock.e_stock_price import StockPriceDaily


class IntervalTwelveData(str, Enum):
    MIN_1 = "1min"
    MIN_5 = "5min"
    MIN_15 = "15min"
    MIN_30 = "30min"
    MIN_45 = "45min"
    HOUR_1 = "1h"
    HOUR_2 = "2h"
    HOUR_4 = "4h"
    HOUR_8 = "8h"
    DAILY = "1day"
    WEEKLY = "1week"
    MONTHLY = "1month"


class StockApi(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    api_client: TDClient = TDClient(apikey=os.getenv("TWELVE_DATA_API_KEY", ""))

    def get_prices(
        self,
        symbol: str,
        interval: IntervalTwelveData = IntervalTwelveData.MIN_5,
        outputsize: Optional[int] = None,
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        timezone: Optional[str] = "America/New_York",
    ) -> Sequence[StockPriceDaily]:
        """
        Documentation: https://github.com/twelvedata/twelvedata-python?tab=readme-ov-file#Time-series
        """

        # Construct the time series
        ts = self.api_client.time_series(
            symbol=symbol,
            interval=interval,
            outputsize=outputsize,
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            timezone=timezone,
        )
        data = ts.as_csv()

        output = []
        for row in data[1:]:
            output.append(
                StockPriceDaily(
                    fk_symbol=symbol,
                    date=datetime.datetime.strptime(row[0], "%Y-%m-%d"),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                ),
            )

        return output
