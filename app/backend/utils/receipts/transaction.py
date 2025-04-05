from datetime import date
from decimal import Decimal

from app.backend.models.db import db
from app.backend.models.e_transaction import Transaction


def get_transaction(transaction_date: date, amount: Decimal) -> Transaction:
    transaction = (
        db.session.query(Transaction)
        .filter(
            db.func.date(Transaction.date) == transaction_date,
            Transaction.amount == amount,
        )
        .first()
    )
    if transaction is None:
        raise ValueError("Transaction not found")
    return transaction
