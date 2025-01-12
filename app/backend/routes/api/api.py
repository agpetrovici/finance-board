import os
from decimal import Decimal
from typing import List

from flask import Blueprint, Response, jsonify


from app.backend.models.db import db
from app.backend.models.transaction import Transaction
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
    amounts: List[Decimal] = list()
    labels: List[str] = list()
    for transaction_pk, month, balance in results:
        amounts.append(balance)
        labels.append(month.strftime("%Y-%m"))
        print(f"Month: {month.strftime('%Y-%m')}, Balance: {balance}")

    # Prepare output
    datasets = [
        {
            "label": "Balance",
            "data": amounts,
            "borderColor": "rgb(75, 192, 192)",
            "tension": 0.1,
        }
    ]

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
