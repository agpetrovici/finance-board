from typing import Any, List, Sequence

from flask_sqlalchemy.session import Session
from sqlalchemy import func, select, Row
from sqlalchemy.orm import scoped_session

from app.backend.models.e_deposit import Deposit
from app.backend.models.e_transaction import Transaction


def get_monthly_transactions(session: scoped_session[Session]) -> Sequence[Row[Any]]:
    # Subquery to get max transaction_pk per month
    subquery = (
        select(
            func.date_trunc("month", Transaction.date).label("month"),
            func.max(Transaction.transaction_pk).label("max_pk"),
        )
        .group_by(Transaction.account_fk, func.date_trunc("month", Transaction.date))
        .subquery()
    )

    # Main query
    query = (
        select(
            Transaction.account_fk,
            Transaction.transaction_pk,
            func.date_trunc("month", Transaction.date).label("month"),
            Transaction.balance,
        )
        .join(subquery, (func.date_trunc("month", Transaction.date) == subquery.c.month) & (Transaction.transaction_pk == subquery.c.max_pk))
        .order_by(Transaction.transaction_pk.asc())
    )
    output = session.execute(query).all()

    return output


def get_deposits() -> List[Deposit]:
    deposits: List[Deposit] = Deposit.query.all()

    return deposits
