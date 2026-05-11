import os
import time
from datetime import datetime
from enum import Enum
from typing import Optional, Sequence

from pydantic import BaseModel
from twelvedata import TDClient
from twelvedata.exceptions import TwelveDataError

from app.backend.models.e_fx_rate import FxRateDaily
from app.backend.models.stock.e_stock_price import StockPriceDaily
from app.backend.models.stock.e_stock_price_15min import StockPrice15min


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

    def get_prices_15min(
        self,
        symbol: str,
        interval: IntervalTwelveData = IntervalTwelveData.MIN_5,
        outputsize: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: Optional[str] = "America/New_York",
    ) -> Sequence[StockPrice15min]:
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
        try:
            data = ts.as_csv()
        except TwelveDataError as e:
            if "Wait for the next minute or consider switching to a higher tier plan" in str(e):
                print("Sleeping for 65 seconds")
                time.sleep(65)
                data = ts.as_csv()
                print("Done sleeping")
            else:
                raise e

        output = []
        for row in data[1:]:
            output.append(
                StockPrice15min(
                    fk_symbol=symbol,
                    datetime=datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                ),
            )

        return output

    def get_prices(
        self,
        symbol: str,
        interval: IntervalTwelveData = IntervalTwelveData.MIN_5,
        outputsize: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
        try:
            data = ts.as_csv()
        except TwelveDataError as e:
            if "Wait for the next minute or consider switching to a higher tier plan" in str(e):
                print("Sleeping for 65 seconds")
                time.sleep(65)
                data = ts.as_csv()
                print("Done sleeping")
            else:
                raise e

        output = []
        for row in data[1:]:
            output.append(
                StockPriceDaily(
                    fk_symbol=symbol,
                    date=datetime.strptime(row[0], "%Y-%m-%d"),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[5]),
                ),
            )

        return output

    def get_earliest_timestamp(
        self,
        symbol: str,
        interval: IntervalTwelveData = IntervalTwelveData.DAILY,
        isin: Optional[str] = None,
        exchange: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> datetime:
        """
        Return the earliest available datetime for the given instrument and interval.

        Documentation: https://twelvedata.com/docs/discovery/earliest-timestamp
        """
        resolved_isin = (isin.strip() if isin else None) or StockPriceDaily.isin_for_symbol(symbol)
        kwargs: dict = {"interval": interval}
        if resolved_isin:
            kwargs["isin"] = resolved_isin
        else:
            kwargs["symbol"] = symbol
        if exchange:
            kwargs["exchange"] = exchange
        if timezone:
            kwargs["timezone"] = timezone

        result = self.api_client.get_earliest_timestamp(**kwargs).as_json()

        raw = result["datetime"]
        fmt = "%Y-%m-%d %H:%M:%S" if " " in raw else "%Y-%m-%d"
        return datetime.strptime(raw, fmt)

    def get_fx_prices(
        self,
        symbol: str,
        interval: IntervalTwelveData = IntervalTwelveData.DAILY,
        outputsize: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timezone: Optional[str] = "UTC",
    ) -> Sequence[FxRateDaily]:
        """Fetch forex OHLC time series (no volume) from Twelve Data."""

        ts = self.api_client.time_series(
            symbol=symbol,
            interval=interval,
            outputsize=outputsize,
            start_date=start_date.strftime("%Y-%m-%d") if start_date else None,
            end_date=end_date.strftime("%Y-%m-%d") if end_date else None,
            timezone=timezone,
        )
        try:
            data = ts.as_csv()
        except TwelveDataError as e:
            if "Wait for the next minute or consider switching to a higher tier plan" in str(e):
                print("Sleeping for 65 seconds")
                time.sleep(65)
                data = ts.as_csv()
                print("Done sleeping")
            else:
                raise e

        output = []
        for row in data[1:]:
            output.append(
                FxRateDaily(
                    currency_pair=symbol,
                    date=datetime.strptime(row[0], "%Y-%m-%d"),
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                ),
            )

        return output
