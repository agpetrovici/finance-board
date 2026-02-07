import os
from datetime import datetime

from binance.client import Client
from sqlalchemy.orm import Session

from app.backend.models.e_balance_crypto import BalanceCrypto


def get_account_balance(session: Session) -> None:
    # Initialize the account
    client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET_KEY"))

    # Fetch account snapshot (SPOT, MARGIN, FUTURES)
    snapshot = client.get_account_snapshot(type="SPOT")

    fk_account_crypto = 1

    # Generate data
    data = []
    for element in snapshot["snapshotVos"]:
        for day in element["data"]["balances"]:
            unix_timestamp = element["updateTime"]
            timestamp = datetime.fromtimestamp(unix_timestamp / 1000)
            balance = BalanceCrypto(
                fk_account_crypto=fk_account_crypto,
                timestamp=timestamp,
                asset=day["asset"],
                free=day["free"],
                locked=day["locked"],
            )
            data.append(balance)

    # For each balance record, update if exists or insert if not
    for balance in data:
        existing = session.query(BalanceCrypto).filter_by(fk_account_crypto=balance.fk_account_crypto, timestamp=balance.timestamp, asset=balance.asset).first()

        if existing:
            existing.free = balance.free
            existing.locked = balance.locked
        else:
            session.add(balance)

    session.commit()
