import csv
import io
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.backend.models.e_transaction import FiatTransaction
from app.backend.models.m_account import Account
from app.backend.routes.imports.utils.get_last_movement import get_last_movement


def get_new_movements_imagin(data: list[FiatTransaction], last_movement: Optional[FiatTransaction], account_pk: int) -> list[FiatTransaction]:
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


def process_imagin(session: Session, file_buffer: io.BytesIO) -> list[FiatTransaction]:
    file_buffer.seek(0)
    file_content = file_buffer.read().decode("utf-8")
    split_text = "Concepto;Fecha;Importe;Saldo disponible"
    csv1, csv2 = file_content.split(split_text)
    csv2 = split_text + csv2
    reader1 = csv.DictReader(csv1.splitlines(), delimiter=";")
    reader2 = csv.DictReader(csv2.splitlines(), delimiter=";")
    data_rows1 = list(reader1)
    data_rows2 = list(reader2)
    data_rows2 = list(reversed(data_rows2))

    iban = data_rows1[0]["IBAN"]
    account = session.query(Account).filter_by(account_number=iban).first()

    last_transaction = get_last_movement(session, account.account_pk)
    transactions = [
        FiatTransaction(
            date=datetime.strptime(x["Fecha"], "%d/%m/%Y"),
            amount=Decimal(x["Importe"].replace(".", "").replace(",", ".").replace("EUR", "")),
            balance=Decimal(x["Saldo disponible"].replace(".", "").replace(",", ".").replace("EUR", "")),
            concept=x["Concepto"].strip(),
            account_fk=account.account_pk,
        )
        for x in data_rows2
    ]
    if last_transaction is None:
        return transactions

    new_movements = get_new_movements_imagin(transactions, last_transaction, account.account_pk)
    return new_movements
