from datetime import date
from decimal import Decimal

from app.backend.models.db import db
from app.backend.models.e_transaction import FiatTransaction


def get_transaction(transaction_date: date, amount: Decimal) -> FiatTransaction:
    transaction = (
        db.session.query(FiatTransaction)
        .filter(
            db.func.date(FiatTransaction.date) == transaction_date,
            FiatTransaction.amount == amount,
        )
        .first()
    )
    if transaction is None:
        raise ValueError("Transaction not found")
    return transaction
