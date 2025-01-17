import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from flask import Blueprint, Response, jsonify

from app.backend.models.m_account import Account
from app.backend.models.db import db
from app.backend.models.e_transaction import Transaction
from app.backend.utils.bank_statement import get_deposits
from app.backend.utils.bank_statement import get_monthly_transactions

# Get the absolute path to the static folder
current_dir = os.path.dirname(os.path.abspath(__file__))
static_folder = os.path.join(current_dir, "static")

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/get-bank-statement", methods=["POST"])
def get_bank_statement() -> Response:
    # Group transactions by date and calculate totals for last day of each month
    results = get_monthly_transactions(db.session)

    # Process results
    # Prepare amount by date
    amount_by_date: Dict[datetime, Dict[int, Decimal]] = dict()
    for transaction in results:
        if transaction[2] not in amount_by_date:
            amount_by_date[transaction[2]] = dict()
        amount_by_date[transaction[2]][transaction[0]] = transaction[3]

    # Prepare amount by account
    labels: List[str] = list()
    accounts_data = Account.query.all()
    accounts_pks = [account.account_pk for account in accounts_data]
    amount_by_account: Dict[int, List[Decimal]] = {account_pk: list() for account_pk in accounts_pks}
    amount_total: List[Decimal] = list()
    for date, row in amount_by_date.items():
        labels.append(date.strftime("%Y-%m"))
        current_amount_subtotal = Decimal("0")
        for account_fk in accounts_pks:
            current_amount = row.get(account_fk, Decimal(0))
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
                "label": f"Account {account_pk}",
                "data": amounts,
                "borderColor": "rgb(75, 192, 192)",
                "tension": 0.1,
            }
        )

    output = {
        "datasets": datasets,
        "labels": labels,
    }
    return jsonify(output)


@bp.route("/get-bank-statement-by-category", methods=["POST"])
def get_bank_statement_by_category() -> Response:
    transactions = Transaction.query.all()

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

    output = {
        "datasets": datasets,
        "labels": labels,
    }
    return jsonify(output)


@bp.route("/test-get-bank-statement", methods=["POST"])
def test_get_bank_statement() -> Response:
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

    output = {
        "datasets": datasets,
        "labels": labels,
    }
    return jsonify(output)
