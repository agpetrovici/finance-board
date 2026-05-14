import datetime

from app.integrations.twelve_data.stock_api import IntervalTwelveData
from etl.get_prices import get_prices
from app.backend.models.stock.e_stock_price import StockPriceDaily
from app.backend.models.e_stock_transaction import StockTransaction


def run() -> None:
    symbols = StockTransaction.get_distinct_symbols_in_portfolio()

    end_date = datetime.datetime.now().date()
    end_date += datetime.timedelta(days=1)
    for ix, symbol in enumerate(symbols):
        # Get start date based on this symbol from StockPriceDaily
        stock_price = StockPriceDaily.get_last_price(symbol)
        if stock_price:
            start_date: datetime.date = stock_price.date.date()
        else:
            # Get the start_date from the first StockTransaction for this symbol
            stock_transaction = StockTransaction.get_first_transaction(symbol)
            if not stock_transaction:
                print(f"{ix} {symbol} has no transactions")
                continue
            start_date = stock_transaction.execution_date.date()

        get_prices(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            interval=IntervalTwelveData.DAILY,
            timezone="UTC",
        )
        print(f"{ix} done {symbol}")
    print("done")


if __name__ == "__main__":
    run()
