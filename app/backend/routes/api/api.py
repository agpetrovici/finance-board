from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from dateutil.rrule import MONTHLY, rrule
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.e_fx_rate import FxRateDaily
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.m_account import Account
from app.backend.models.portfolio.portfolio import Portfolio
from app.backend.models.portfolio.stock import Stock
from app.backend.models.stock.e_stock_price import StockPriceDaily
from app.backend.routes.api.apex import ApexAreaChartData, IncomeAndExpensesStatement
from app.backend.utils.bank_statement import get_deposits, get_monthly_transactions
from app.backend.utils.stock.calculate_portfolio import calculate_portfolio
from app.backend.utils.transaction_series import (
    get_income_expenses_statements,
    get_stock_transaction_series,
    get_transaction_series,
    test_get_transaction_series,
)

router = APIRouter(prefix="/api", tags=["api"])



@router.post("/get-transaction-by-day")
def get_transaction_by_day(session: Session = Depends(get_db)) -> dict[str, Any]:
    output = get_transaction_series(session)
    return output.to_dict()


@router.post("/test-get-transaction-by-day")
def test_get_transaction_by_day() -> dict[str, Any]:
    output = test_get_transaction_series()
    return output.to_dict()


@router.post("/get-stock-statement")
def get_stock_transactions(session: Session = Depends(get_db)) -> dict[str, Any]:
    output = get_stock_transaction_series(session)
    return output.to_dict()


@router.post("/get-financial-series")
def get_financial_series(session: Session = Depends(get_db)) -> dict[str, Any]:
    """Return ApexCharts-compatible series for the financial overview chart.

    Each account becomes a series with ``[date, balance]`` data points.
    A "Total" series is prepended.
    """
    transactions = get_monthly_transactions(session)
    deposits = get_deposits(session)

    amount_by_date: Dict[datetime, Dict[int, Decimal]] = {}
    min_transaction_date = min(t[2] for t in transactions)
    max_transaction_date = max(t[2] for t in transactions)

    if deposits:
        min_deposit_date = min(d.date_start.replace(day=1) for d in deposits)
        max_deposit_date = max(d.date_end.replace(day=1) for d in deposits)
        min_date = min(min_transaction_date, min_deposit_date)
        max_date = max(max_transaction_date, max_deposit_date)
    else:
        min_date = min_transaction_date
        max_date = max_transaction_date

    for date in rrule(MONTHLY, dtstart=min_date, until=max_date):
        amount_by_date.setdefault(date, {})

    for t in transactions:
        amount_by_date[t[2]][t[0]] = t[3]

    for deposit in deposits:
        start = deposit.date_start.replace(day=1)
        end = deposit.date_end.replace(day=1)
        for date in rrule(MONTHLY, dtstart=start, until=end):
            amount_by_date[date][deposit.fk_account] = deposit.balance
        amount_by_date[end][deposit.fk_account] = deposit.balance + deposit.interest_maturity

    accounts_data = session.query(Account).all()
    accounts_pks = {a.account_pk: a for a in accounts_data}
    prev_amount: Dict[int, Decimal] = {pk: Decimal("0") for pk in accounts_pks}

    total_points: List[list] = []
    account_points: Dict[int, List[list]] = {pk: [] for pk in accounts_pks}

    for date in sorted(amount_by_date):
        row = amount_by_date[date]
        current_total = Decimal("0")
        for pk in accounts_pks:
            amount = row.get(pk, prev_amount[pk])
            prev_amount[pk] = amount
            current_total += amount
            account_points[pk].append([date.strftime("%Y-%m-%d"), float(round(amount, 2))])
        total_points.append([date.strftime("%Y-%m-%d"), float(round(current_total, 2))])

    series: List[dict] = [{"name": "Total", "data": total_points}]
    for pk, points in account_points.items():
        series.append({"name": accounts_pks[pk].name, "data": points})

    output = ApexAreaChartData(series)
    return output.to_dict()


@router.post("/get-income-expenses")
def get_income_expenses(session: Session = Depends(get_db)) -> list[IncomeAndExpensesStatement]:
    return get_income_expenses_statements(session)


@router.post("/get-portfolio-performance")
def get_portfolio_performance(session: Session = Depends(get_db)) -> dict[str, Any]:
    """Return comprehensive portfolio performance data for all charts.

    Normalises all transaction values to USD before computing metrics.
    Transactions already in USD are used as-is; others are converted via
    daily FX rates from ``e_fx_rate_daily`` (e.g. pair ``"EUR/USD"``).
    """
    stock_transactions = session.query(StockTransaction).all()
    if not stock_transactions:
        return _empty_performance_response()

    used_symbols = list({tx.fk_symbol for tx in stock_transactions if tx.fk_symbol})
    stock_prices = (
        session.query(StockPriceDaily)
        .filter(StockPriceDaily.fk_symbol.in_(used_symbols))
        .order_by(StockPriceDaily.date.asc())
        .all()
    )

    fx_rates = _build_fx_lookup(stock_transactions, session)
    portfolio = calculate_portfolio(stock_transactions, stock_prices, fx_rates)
    return _build_performance_response(portfolio)


def _build_fx_lookup(
    transactions: list[StockTransaction],
    session: Session,
) -> dict[str, dict[datetime.date, float]]:
    """Build ``{pair: {date: close_rate}}`` for every non-USD broker currency."""
    non_usd = {
        tx.value_broker_currency
        for tx in transactions
        if tx.value_broker_currency and tx.value_broker_currency != "USD"
    }
    if not non_usd:
        return {}

    dates = [
        (
            tx.execution_date.date()
            if isinstance(tx.execution_date, datetime)
            else tx.execution_date
        )
        for tx in transactions
    ]
    min_date, max_date = min(dates), max(dates)

    lookup: dict[str, dict[datetime.date, float]] = {}
    for currency in non_usd:
        pair = f"{currency}/USD"
        rates = FxRateDaily.get_rates(pair, min_date, max_date, session)
        lookup[pair] = {
            (
                r.date.date()
                if isinstance(r.date, datetime)
                else r.date
            ): r.close
            for r in rates
        }
    return lookup


def _empty_performance_response() -> dict[str, Any]:
    return {
        "summary": {
            "total_invested": 0,
            "total_cash_returned": 0,
            "net_invested": 0,
            "total_market_value": 0,
            "total_unrealized_pnl": 0,
            "total_realized_pnl": 0,
            "total_return": 0,
            "total_return_pct": 0,
        },
        "value_vs_cost": {"series": []},
        "pnl_series": {"series": []},
        "stock_performance": [],
        "allocation": [],
        "per_stock_series": {},
        "monthly_returns": {"categories": [], "values": []},
    }


def _build_performance_response(portfolio: Portfolio) -> dict[str, Any]:
    total_stock = next(
        (s for s in portfolio.stocks if s.symbol == "Total"), None
    )
    individual_stocks = [s for s in portfolio.stocks if s.symbol != "Total"]

    def _ts(dt: Any) -> int:
        return int(dt.timestamp() * 1000)

    # Chart 1: Value vs Cost Basis
    value_vs_cost: dict[str, Any] = {"series": []}
    if total_stock and total_stock.values:
        value_vs_cost = {
            "series": [
                {
                    "name": "Market Value",
                    "data": [
                        [_ts(v.date), round(v.value, 2)]
                        for v in total_stock.values
                    ],
                },
                {
                    "name": "Cost Basis",
                    "data": [
                        [_ts(v.date), round(v.cost_basis, 2)]
                        for v in total_stock.values
                    ],
                },
            ]
        }

    # Chart 2: Cumulative P&L
    pnl_series: dict[str, Any] = {"series": []}
    if total_stock and total_stock.values:
        pnl_series = {
            "series": [
                {
                    "name": "Unrealized P&L",
                    "data": [
                        [_ts(v.date), round(v.unrealized_pnl, 2)]
                        for v in total_stock.values
                    ],
                },
                {
                    "name": "Realized P&L",
                    "data": [
                        [_ts(v.date), round(v.realized_pnl, 2)]
                        for v in total_stock.values
                    ],
                },
                {
                    "name": "Total P&L",
                    "data": [
                        [_ts(v.date), round(v.total_pnl, 2)]
                        for v in total_stock.values
                    ],
                },
            ]
        }

    # Chart 3: Per-stock performance
    stock_performance: list[dict[str, Any]] = []
    for stock in individual_stocks:
        if not stock.values:
            continue
        latest = stock.values[-1]
        return_pct = (
            (latest.total_pnl / latest.cost_basis * 100)
            if latest.cost_basis > 0
            else 0.0
        )
        stock_performance.append(
            {
                "symbol": stock.symbol,
                "return_pct": round(return_pct, 2),
                "total_pnl": round(latest.total_pnl, 2),
                "market_value": round(latest.value, 2),
                "cost_basis": round(latest.cost_basis, 2),
            }
        )
    stock_performance.sort(key=lambda x: x["return_pct"], reverse=True)

    # Chart 4: Allocation
    total_value = sum(sp["market_value"] for sp in stock_performance)
    allocation = [
        {
            "symbol": sp["symbol"],
            "value": sp["market_value"],
            "weight": round(
                sp["market_value"] / total_value * 100 if total_value > 0 else 0.0,
                2,
            ),
        }
        for sp in stock_performance
    ]

    # Chart 5: Per-stock series
    per_stock_series: dict[str, dict[str, list]] = {}
    for stock in individual_stocks:
        per_stock_series[stock.symbol] = {
            "market_value": [
                [_ts(v.date), round(v.value, 2)] for v in stock.values
            ],
            "cost_basis": [
                [_ts(v.date), round(v.cost_basis, 2)] for v in stock.values
            ],
        }

    # Chart 6: Monthly returns
    monthly_returns = _compute_monthly_returns(total_stock)

    return {
        "summary": {
            "total_invested": round(portfolio.total_invested, 2),
            "total_cash_returned": round(portfolio.total_cash_returned, 2),
            "net_invested": round(portfolio.net_invested, 2),
            "total_market_value": round(portfolio.total_market_value, 2),
            "total_unrealized_pnl": round(portfolio.total_unrealized_pnl, 2),
            "total_realized_pnl": round(portfolio.total_realized_pnl, 2),
            "total_return": round(portfolio.total_return, 2),
            "total_return_pct": round(portfolio.total_return_pct, 2),
        },
        "value_vs_cost": value_vs_cost,
        "pnl_series": pnl_series,
        "stock_performance": stock_performance,
        "allocation": allocation,
        "per_stock_series": per_stock_series,
        "monthly_returns": monthly_returns,
    }


def _compute_monthly_returns(total_stock: Stock | None) -> dict[str, Any]:
    if not total_stock or not total_stock.values:
        return {"categories": [], "values": []}

    month_end_pnl: dict[str, float] = {}
    for v in total_stock.values:
        month_key = v.date.strftime("%Y-%m")
        month_end_pnl[month_key] = v.total_pnl

    sorted_months = sorted(month_end_pnl.keys())
    categories: list[str] = []
    values: list[float] = []
    prev_pnl = 0.0

    for month in sorted_months:
        pnl = month_end_pnl[month]
        categories.append(month)
        values.append(round(pnl - prev_pnl, 2))
        prev_pnl = pnl

    return {"categories": categories, "values": values}
