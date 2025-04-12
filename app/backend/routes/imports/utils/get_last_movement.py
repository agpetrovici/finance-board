from typing import Optional

from app.backend.models.db import db
from app.backend.models.e_transaction import FiatTransaction


def get_last_movement(account_pk: int) -> Optional[FiatTransaction]:
    last_movement = db.session.query(FiatTransaction).filter(FiatTransaction.account_fk == account_pk).order_by(FiatTransaction.transaction_pk.desc()).first()
    if isinstance(last_movement, FiatTransaction):
        return last_movement
    else:
        return None
