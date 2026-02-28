from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from dateutil.rrule import MONTHLY, rrule
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.m_account import Account
from app.backend.routes.api.apex import ApexAreaChartData
from app.backend.utils.bank_statement import get_deposits, get_monthly_transactions
from app.backend.utils.transaction_series import get_stock_transaction_series, get_transaction_series, test_get_transaction_series

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

    Each account becomes a series with ``[timestamp_ms, balance]`` data points.
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
        ts_ms = int(date.timestamp() * 1000)
        current_total = Decimal("0")
        for pk in accounts_pks:
            amount = row.get(pk, prev_amount[pk])
            prev_amount[pk] = amount
            current_total += amount
            account_points[pk].append([ts_ms, float(round(amount, 2))])
        total_points.append([ts_ms, float(round(current_total, 2))])

    series: List[dict] = [{"name": "Total", "data": total_points}]
    for pk, points in account_points.items():
        series.append({"name": accounts_pks[pk].name, "data": points})

    output = ApexAreaChartData(series)
    return output.to_dict()
