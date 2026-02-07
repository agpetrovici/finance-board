import io
from datetime import datetime
from decimal import Decimal
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

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


def df_to_FiatTransaction(df: pd.DataFrame, account_fk: int) -> list[FiatTransaction]:
    data = []

    # We need to find dynamically the row where the actual values begin since the header may contain pending orders
    ix_of_values = None
    for ix, row in df.iterrows():
        if row[0] == "Fecha contable" and row[1] == "Fecha valor" and row[2] == "Descripción" and row[3] == "Importe" and row[4] == "Saldo" and row[5] == "Divisa":
            ix_of_values = ix
            ix_of_values += 1  # So it begins at the next row, not at the title itself
    if ix_of_values is None:
        raise Exception("The format of the excel file has changed !")

    for ix, row in df.loc[ix_of_values:].iterrows():
        data.append(
            FiatTransaction(
                balance=Decimal(row[4]),
                account_fk=account_fk,
                amount=Decimal(row[3]),
                date=datetime.strptime(row[1], "%d/%m/%Y"),
                concept=row[2],
            )
        )
    data = data[::-1]
    return data


def process_bankinter(session: Session, file_buffer: io.BytesIO) -> list[FiatTransaction]:
    df = pd.read_excel(file_buffer, header=None, dtype="str")
    iban_str = df.iloc[0, 0]
    iban = iban_str.split("MOVIMIENTOS DE LA CUENTA ")[-1]
    account = session.query(Account).filter_by(account_number=iban).first()
    if account is None:
        return None
    last_transaction = get_last_movement(session, account.account_pk)
    transactions = df_to_FiatTransaction(df, account.account_pk)
    if last_transaction is None:
        return transactions

    new_movements = get_new_movements_bankinter(transactions, last_transaction, account.account_pk)
    return new_movements
