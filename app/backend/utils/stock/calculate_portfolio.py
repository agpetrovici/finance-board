import datetime
from collections import defaultdict
from typing import Sequence

from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.portfolio.portfolio import Portfolio
from app.backend.models.portfolio.stock import Stock
from app.backend.models.portfolio.stock_value import StockValue
from app.backend.models.stock.e_stock_price import StockPriceDaily

ORDER_CLASS_BUY = 1
ORDER_CLASS_SELL = 2


def _to_usd(
    value: float,
    currency: str,
    date: datetime.date,
    fx_rates: dict[str, dict[datetime.date, float]],
) -> float:
    """Convert *value* to USD.  Returns *value* unchanged when already USD."""
    if currency == "USD":
        return value
    pair = f"{currency}/USD"
    pair_rates = fx_rates.get(pair)
    if not pair_rates:
        return value
    rate = pair_rates.get(date)
    if rate is None:
        prior = [d for d in pair_rates if d <= date]
        rate = pair_rates[max(prior)] if prior else None
    return value * rate if rate is not None else value


def calculate_portfolio(
    transactions: Sequence[StockTransaction],
    prices: Sequence[StockPriceDaily],
    fx_rates: dict[str, dict[datetime.date, float]] | None = None,
) -> Portfolio:
    """Calculate the daily portfolio value and performance metrics.

    Uses Weighted Average Cost (WAC) for cost basis tracking.  On each buy
    the average cost is recomputed; on each sell the cost allocated to the
    sold shares equals ``qty * avg_cost`` (the average stays unchanged).

    All values are normalised to USD.  When ``fx_rates`` is provided,
    transactions whose ``value_broker_currency`` is not USD are converted
    using the daily close rate for the corresponding pair (e.g. EUR/USD).

    Args:
        transactions: All stock transactions (buys and sells).
        prices: Daily closing prices for the relevant symbols.
        fx_rates: Optional ``{pair: {date: rate}}`` lookup built from
            ``e_fx_rate_daily``.  Pass *None* when all transactions are
            already in USD.

    Returns:
        A ``Portfolio`` with per-symbol ``Stock`` entries (including a
        synthetic *Total* series) and portfolio-level summary metrics.
    """

    # -- 1. Build price lookup: {symbol: {date: close_price}} ---------------
    price_lookup: dict[str, dict[datetime.date, float]] = defaultdict(dict)
    all_dates: set[datetime.date] = set()

    for p in prices:
        d = p.date.date() if isinstance(p.date, datetime.datetime) else p.date
        price_lookup[p.fk_symbol][d] = p.close
        all_dates.add(d)

    sorted_dates = sorted(all_dates)

    # -- 2. Build per-symbol transaction list --------------------------------
    # {symbol: {date: [(order_class, quantity, total_user_value), ...]}}
    tx_by_symbol: dict[str, dict[datetime.date, list[tuple[int, int, float]]]] = (
        defaultdict(lambda: defaultdict(list))
    )

    portfolio_total_invested = 0.0
    portfolio_total_cash_returned = 0.0

    for tx in transactions:
        symbol = tx.fk_symbol
        if symbol is None:
            continue
        if symbol not in price_lookup:
            continue
        d = (
            tx.execution_date.date()
            if isinstance(tx.execution_date, datetime.datetime)
            else tx.execution_date
        )
        total_val = float(tx.value_broker)
        if fx_rates:
            total_val = _to_usd(total_val, tx.value_broker_currency, d, fx_rates)
        tx_by_symbol[symbol][d].append((tx.fk_order_class, tx.quantity, total_val))

        if tx.fk_order_class == ORDER_CLASS_BUY:
            portfolio_total_invested += abs(total_val)
        else:
            portfolio_total_cash_returned += abs(total_val)

    # Process buys before sells on same date so avg cost is up-to-date
    for symbol_txs in tx_by_symbol.values():
        for d_txs in symbol_txs.values():
            d_txs.sort(key=lambda t: t[0])

    # -- 3. Walk dates and compute daily StockValue with WAC metrics ---------
    all_symbols = set(price_lookup.keys()) | set(tx_by_symbol.keys())
    stocks: list[Stock] = []

    for symbol in sorted(all_symbols):
        symbol_prices = price_lookup.get(symbol, {})
        symbol_txs = tx_by_symbol.get(symbol, {})

        running_qty = 0
        running_cost_basis = 0.0
        cumulative_realized_pnl = 0.0
        values: list[StockValue] = []

        for d in sorted_dates:
            if d in symbol_txs:
                for order_class, qty, total_val in symbol_txs[d]:
                    if order_class == ORDER_CLASS_BUY:
                        running_cost_basis += total_val
                        running_qty += qty
                    elif order_class == ORDER_CLASS_SELL:
                        avg_cost = (
                            running_cost_basis / running_qty
                            if running_qty > 0
                            else 0.0
                        )
                        cost_of_sold = qty * avg_cost
                        cumulative_realized_pnl += total_val - cost_of_sold
                        running_cost_basis -= cost_of_sold
                        running_qty -= qty

            if running_qty > 0 and d in symbol_prices:
                price = symbol_prices[d]
                abs_cost = abs(running_cost_basis)
                avg_cost = abs_cost / running_qty if running_qty > 0 else 0.0
                market_value = running_qty * price
                unrealized = market_value - abs_cost
                unrealized_pct = (
                    (unrealized / abs_cost * 100) if abs_cost > 0 else 0.0
                )
                total_pnl = unrealized + cumulative_realized_pnl

                values.append(
                    StockValue(
                        date=datetime.datetime.combine(d, datetime.time.min),
                        quantity=running_qty,
                        price=price,
                        value=market_value,
                        cost_basis=abs_cost,
                        avg_cost_per_share=avg_cost,
                        unrealized_pnl=unrealized,
                        unrealized_pnl_pct=unrealized_pct,
                        realized_pnl=cumulative_realized_pnl,
                        total_pnl=total_pnl,
                    )
                )

        if values:
            stocks.append(Stock(symbol=symbol, values=values))

    # -- 4. Compute "Total" synthetic series ---------------------------------
    stock_value_by_date: dict[str, dict[datetime.date, StockValue]] = {}
    for stock in stocks:
        stock_value_by_date[stock.symbol] = {
            v.date.date(): v for v in stock.values
        }

    daily_totals: list[StockValue] = []
    for d in sorted_dates:
        total_value = 0.0
        total_cost = 0.0
        total_unrealized = 0.0
        total_realized = 0.0

        for stock in stocks:
            val = stock_value_by_date[stock.symbol].get(d)
            if val:
                total_value += val.value
                total_cost += val.cost_basis
                total_unrealized += val.unrealized_pnl
                total_realized += val.realized_pnl

        if total_value > 0:
            t_pnl = total_unrealized + total_realized
            daily_totals.append(
                StockValue(
                    date=datetime.datetime.combine(d, datetime.time.min),
                    quantity=0,
                    price=0.0,
                    value=total_value,
                    cost_basis=total_cost,
                    avg_cost_per_share=0.0,
                    unrealized_pnl=total_unrealized,
                    unrealized_pnl_pct=(
                        (total_unrealized / total_cost * 100)
                        if total_cost > 0
                        else 0.0
                    ),
                    realized_pnl=total_realized,
                    total_pnl=t_pnl,
                )
            )

    stocks.append(Stock(symbol="Total", values=daily_totals))

    # Sort by highest latest value descending
    if len(stocks) > 1:
        stocks.sort(
            key=lambda s: s.values[-1].value if s.values else 0.0,
            reverse=True,
        )

    # -- 5. Portfolio-level summary ------------------------------------------
    latest_total = daily_totals[-1] if daily_totals else None

    total_market_value = latest_total.value if latest_total else 0.0
    total_unrealized_pnl = latest_total.unrealized_pnl if latest_total else 0.0
    total_realized_pnl = latest_total.realized_pnl if latest_total else 0.0
    total_return = latest_total.total_pnl if latest_total else 0.0
    net_invested = portfolio_total_invested - portfolio_total_cash_returned
    total_return_pct = (
        (total_return / portfolio_total_invested * 100)
        if portfolio_total_invested > 0
        else 0.0
    )

    return Portfolio(
        stocks=stocks,
        total_invested=portfolio_total_invested,
        total_cash_returned=portfolio_total_cash_returned,
        net_invested=net_invested,
        total_market_value=total_market_value,
        total_unrealized_pnl=total_unrealized_pnl,
        total_realized_pnl=total_realized_pnl,
        total_return=total_return,
        total_return_pct=total_return_pct,
    )
