import datetime
from collections import defaultdict
from typing import Sequence

from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.portfolio.portfolio import Portfolio
from app.backend.models.portfolio.stock import Stock
from app.backend.models.portfolio.stock_value import StockValue
from app.backend.models.stock.e_stock_price import StockPriceDaily

# Order class IDs matching m_order_class (compra=1, venta=2)
ORDER_CLASS_BUY = 1
ORDER_CLASS_SELL = 2


def calculate_portfolio(
    transactions: Sequence[StockTransaction],
    prices: Sequence[StockPriceDaily],
) -> Portfolio:
    """Calculate the daily portfolio value for each stock.

    Walks through every trading day present in ``prices``. For each day it
    applies any transactions that occurred on that date (buys add shares,
    sells remove them) and records the resulting position valued at the
    closing price.

    Args:
        transactions: All stock transactions (buys and sells).
        prices: Daily closing prices for the relevant symbols.
        isin_to_symbol: Mapping from ISIN to ticker symbol so that
            transactions (keyed by ISIN) can be matched to prices
            (keyed by symbol).

    Returns:
        A ``Portfolio`` with one ``Stock`` entry per symbol that was held
        at any point, each containing the daily ``StockValue`` series.
    """

    # -- 1. Build price lookup: {symbol: {date: close_price}} ---------------
    price_lookup: dict[str, dict[datetime.date, float]] = defaultdict(dict)
    all_dates: set[datetime.date] = set()

    for p in prices:
        d = p.date.date() if isinstance(p.date, datetime.datetime) else p.date
        price_lookup[p.fk_symbol][d] = p.close
        all_dates.add(d)

    sorted_dates = sorted(all_dates)

    # -- 2. Build per-symbol transaction deltas: {symbol: {date: qty_delta}} -
    tx_deltas: dict[str, dict[datetime.date, int]] = defaultdict(lambda: defaultdict(int))

    for tx in transactions:
        symbol = tx.fk_symbol
        if symbol is None:
            continue
        d = tx.execution_date.date() if isinstance(tx.execution_date, datetime.datetime) else tx.execution_date
        delta = tx.quantity if tx.fk_order_class == ORDER_CLASS_BUY else -tx.quantity
        tx_deltas[symbol][d] += delta

    # -- 3. Walk dates and compute daily StockValue per symbol ---------------
    all_symbols = set(price_lookup.keys()) | set(tx_deltas.keys())
    stocks: list[Stock] = []

    for symbol in sorted(all_symbols):
        symbol_prices = price_lookup.get(symbol, {})
        symbol_tx = tx_deltas.get(symbol, {})
        running_quantity = 0
        values: list[StockValue] = []

        for d in sorted_dates:
            # Apply any transactions on this day
            running_quantity += symbol_tx.get(d, 0)

            # Only record days where there is a position and a known price
            if running_quantity > 0 and d in symbol_prices:
                price = symbol_prices[d]
                values.append(
                    StockValue(
                        date=datetime.datetime.combine(d, datetime.time.min),
                        quantity=running_quantity,
                        price=price,
                        value=running_quantity * price,
                    )
                )

        if values:
            stocks.append(Stock(symbol=symbol, values=values))
    portfolio=Portfolio(stocks=stocks)


    # Compute total portfolio value for each day
    daily_totals = []
    for d in sorted_dates:
        total = 0.0
        for stock in stocks:
            # Find StockValue for this day, if exists
            val = next((v for v in stock.values if v.date.date() == d), None)
            if val:
                total += val.value
        if total > 0:
            daily_totals.append(
                StockValue(
                    date=datetime.datetime.combine(d, datetime.time.min),
                    quantity=0,  # Not meaningful for total, could also use None if StockValue/serialization allows
                    price=0.0,   # Not meaningful for total
                    value=total
                )
            )
    portfolio.stocks.append(Stock(symbol="Total", values=daily_totals))

    # Sort portfolio.stocks by highest latest value descending
    if len(portfolio.stocks) > 1:
        def latest_value(stock):
            if stock.values:
                return stock.values[-1].value
            return 0.0
        portfolio.stocks.sort(key=latest_value, reverse=True)

    return portfolio
