from typing import Optional

from app.backend.models.db import db
from app.backend.models.e_transaction import Transaction


def get_last_movement(account_pk: int) -> Optional[Transaction]:
    last_movement = db.session.query(Transaction).filter(Transaction.account_fk == account_pk).order_by(Transaction.transaction_pk.desc()).first()
    if isinstance(last_movement, Transaction):
        return last_movement
    else:
        return None
