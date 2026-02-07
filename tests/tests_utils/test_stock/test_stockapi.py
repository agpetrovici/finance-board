import datetime
from app.backend.utils.stock.stock_api import StockApi, IntervalTwelveData


def test_get_prices():
    stock_api = StockApi()
    prices = stock_api.get_prices(
        "IBM",
        IntervalTwelveData.DAILY,
        start_date=datetime.datetime.now() - datetime.timedelta(days=365),
        end_date=datetime.datetime.now(),
        timezone="UTC",
    )

    assert prices is not None
