from typing import Optional

from sqlalchemy.orm import Session

from app.backend.models.e_transaction import FiatTransaction


def get_last_movement(session: Session, account_pk: int) -> Optional[FiatTransaction]:
    last_movement = session.query(FiatTransaction).filter(FiatTransaction.account_fk == account_pk).order_by(FiatTransaction.transaction_pk.desc()).first()
    if isinstance(last_movement, FiatTransaction):
        return last_movement
    else:
        return None
