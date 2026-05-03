import datetime

from app.integrations.twelve_data.stock_api import IntervalTwelveData
from etl.get_prices import get_prices
from app.backend.models.stock.e_stock_price import StockPriceDaily
from app.backend.models.e_stock_transaction import StockTransaction

if __name__ == "__main__":
    # Get all transacted symbols
    symbols = StockTransaction.get_distinct_symbols()

    end_date = datetime.datetime.now().date()
    end_date += datetime.timedelta(days=1)
    for ix, symbol in enumerate(symbols):
        # Get start date based on this symbol from StockPriceDaily
        stock_price = StockPriceDaily.get_last_price(symbol)
        if not stock_price:
            print(f"{ix} {symbol} has no prices")
            continue
        start_date:datetime.date = stock_price.date.date()

        get_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=IntervalTwelveData.DAILY,
            timezone="UTC",
        )
        print(f"{ix} done {symbol}")
    print("done")
