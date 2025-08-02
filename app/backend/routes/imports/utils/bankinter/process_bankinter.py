import io
from datetime import datetime
from typing import Optional

import pandas as pd

from app.backend.models.e_transaction import FiatTransaction
from app.backend.models.m_account import Account
from app.backend.routes.imports.utils.get_last_movement import get_last_movement


def get_new_movements_bankinter(data: list[FiatTransaction], last_movement: Optional[FiatTransaction], account_pk: int) -> list[FiatTransaction]:
    movements = []
    get_movements = False

    if last_movement is None:
        get_movements = True

    for transaction in data:
        if get_movements:
            pass
        elif (
            isinstance(last_movement, FiatTransaction)
            and transaction.amount == last_movement.amount
            and transaction.date == last_movement.date
            and transaction.balance == last_movement.balance
        ):
            get_movements = True
            continue
        if get_movements:
            movements.append(transaction)
    return movements


def df_to_FiatTransaction(df: pd.DataFrame, account_fk: int) -> FiatTransaction:
    data = []
    for ix, row in df.loc[4:].iterrows():
        data.append(
            FiatTransaction(
                balance=row[4],
                account_fk=account_fk,
                amount=row[3],
                date=datetime.strptime(row[1], "%d/%m/%Y").date(),
                concept=row[2],
            )
        )
    return data


def process_bankinter(file_buffer: io.BytesIO) -> list[FiatTransaction]:
    df = pd.read_excel(file_buffer, header=None)
    iban_str = df.iloc[0, 0]
    iban = iban_str.split("IBAN: ")[-1]
    account = Account.query.filter_by(account_number=iban).first()
    if account is None:
        return None
    last_transaction = get_last_movement(account.account_pk)
    transactions = df_to_FiatTransaction(df, account.account_pk)
    if last_transaction is None:
        return transactions

    new_movements = get_new_movements_bankinter(transactions, last_transaction, account.account_pk)
    return new_movements
