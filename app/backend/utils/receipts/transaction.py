from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.backend.models.e_transaction import FiatTransaction


def get_transaction(session: Session, transaction_date: date, amount: Decimal) -> FiatTransaction:
    transaction = (
        session.query(FiatTransaction)
        .filter(
            func.date(FiatTransaction.date) == transaction_date,
            FiatTransaction.amount == amount,
        )
        .first()
    )
    if transaction is None:
        raise ValueError("Transaction not found")
    return transaction
