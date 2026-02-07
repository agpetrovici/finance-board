from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List

from dateutil.rrule import MONTHLY, rrule
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.e_transaction import FiatTransaction
from app.backend.models.m_account import Account
from app.backend.routes.api.apex import ApexLineChartData
from app.backend.utils.bank_statement import get_deposits, get_monthly_transactions
from app.backend.utils.transaction_series import get_stock_transaction_series, get_transaction_series, test_get_transaction_series

router = APIRouter(prefix="/api", tags=["api"])


@router.post("/get-bank-statement")
def get_bank_statement(session: Session = Depends(get_db)) -> dict[str, Any]:
    # Group transactions by date and calculate totals for last day of each month
    transactions = get_monthly_transactions(session)
    deposits = get_deposits(session)

    # Prepare amount by date
    amount_by_date: Dict[datetime, Dict[int, Decimal]] = dict()
    # Prepare amount_by_date based on transaction and deposit data
    min_transaction_date = min(transaction[2] for transaction in transactions)
    max_transaction_date = max(transaction[2] for transaction in transactions)

    if deposits:
        min_deposit_date = min(deposit.date_start.replace(day=1) for deposit in deposits)
        max_deposit_date = max(deposit.date_end.replace(day=1) for deposit in deposits)
        min_date = min(min_transaction_date, min_deposit_date)
        max_date = max(max_transaction_date, max_deposit_date)
    else:
        min_date = min_transaction_date
        max_date = max_transaction_date

    for date in rrule(MONTHLY, dtstart=min_date, until=max_date):
        if date not in amount_by_date:
            amount_by_date[date] = dict()
    # Add transaction data
    for transaction in transactions:
        amount_by_date[transaction[2]][transaction[0]] = transaction[3]
    # Add deposit data
    for deposit in deposits:
        deposit_date_start = deposit.date_start.replace(day=1)
        deposit_date_end = deposit.date_end.replace(day=1)
        for date in rrule(MONTHLY, dtstart=deposit_date_start, until=deposit_date_end):
            amount_by_date[date][deposit.fk_account] = deposit.balance
        amount_by_date[deposit_date_end][deposit.fk_account] = deposit.balance + deposit.interest_maturity

    # Prepare amount by account
    labels: List[str] = list()
    accounts_data = session.query(Account).all()
    accounts_pks = {account.account_pk: account for account in accounts_data}
    amount_by_account: Dict[int, List[Decimal]] = {account_pk: list() for account_pk in accounts_pks}
    amount_total: List[Decimal] = list()
    for date, row in amount_by_date.items():
        labels.append(date.strftime("%Y-%m"))
        current_amount_subtotal = Decimal("0")
        for account_fk in accounts_pks.keys():
            # Get current amount, or use previous month's value if None
            current_amount = row.get(account_fk)
            if current_amount is None:
                # Use the previous value from amount_by_account if available
                if amount_by_account[account_fk]:
                    current_amount = amount_by_account[account_fk][-1]
                else:
                    current_amount = Decimal("0")
            current_amount_subtotal += current_amount
            amount_by_account[account_fk].append(current_amount)
        amount_total.append(current_amount_subtotal)

    # Prepare output
    datasets = [
        {
            "label": "Total",
            "data": amount_total,
            "borderColor": "#6EB5FF",
            "tension": 0.1,
        }
    ]

    for account_pk, amounts in amount_by_account.items():
        datasets.append(
            {
                "label": f"{accounts_pks[account_pk].name}",
                "data": amounts,
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1,
            }
        )

    output = ApexLineChartData(labels, datasets)
    return output.to_dict()


@router.post("/get-bank-statement-by-category")
def get_bank_statement_by_category(session: Session = Depends(get_db)) -> dict[str, Any]:
    transactions = session.query(FiatTransaction).all()

    days = list(set(transaction.date for transaction in transactions if transaction.date))
    days.sort()
    labels = [day.strftime("%Y-%m-%d") for day in days]

    transaction_data = dict()
    for day in days:
        transaction_data[day] = {"label": day.strftime("%Y-%m-%d"), "income": 0, "expense": 0}

    for transaction in transactions:
        if transaction.amount > 0:
            transaction_data[transaction.date]["income"] += transaction.amount
        else:
            transaction_data[transaction.date]["expense"] += abs(transaction.amount)

    incomes = [transaction_data[day]["income"] for day in days]
    expenses = [transaction_data[day]["expense"] for day in days]

    # Prepare output
    datasets = [
        {
            "label": "Income",
            "data": incomes,
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1,
        },
        {
            "label": "Expenses",
            "data": expenses,
            "borderColor": "rgb(255, 99, 132)",
            "tension": 0.1,
        },
    ]

    output = ApexLineChartData(labels, datasets)
    return output.to_dict()


@router.post("/test-get-bank-statement")
def test_get_bank_statement() -> dict[str, Any]:
    datasets = [
        {
            "label": "Income",
            "data": [1500, 2000, 1800, 2200, 2600, 2400],
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1,
        },
        {
            "label": "Expenses",
            "data": [1200, 1800, 1600, 2000, 2200, 2100],
            "borderColor": "rgb(255, 99, 132)",
            "tension": 0.1,
        },
    ]

    labels = ["January", "February", "March", "April", "May", "June"]

    output = ApexLineChartData(labels, datasets)
    return output.to_dict()


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
