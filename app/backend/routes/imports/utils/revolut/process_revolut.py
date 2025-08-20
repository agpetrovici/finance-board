import logging
from typing import Any, List

from app.backend.models.e_transaction import FiatTransaction
from app.backend.models.m_account import Account
from app.backend.routes.imports.utils.get_last_movement import get_last_movement
from app.backend.routes.imports.utils.revolut.models import RevolutTransaction


def get_new_movements_revolut(data: List[dict[str, Any]], accounts: List[Account]) -> list[FiatTransaction]:
    transactions: list[RevolutTransaction] = RevolutTransaction.from_dict(data)
    valid_transactions: list[RevolutTransaction] = []
    for x in transactions:
        if x.state == "COMPLETED":
            valid_transactions.append(x)
        elif x.state == "DECLINED":
            logging.error(f"Transaction ({x}) was DECLINED !")
        else:
            logging.error(f"Transaction ({x}) was not handled !")
    movements = []
    account_data = {}
    for x in accounts:
        if x.bank_id is not None:
            last_movement = get_last_movement(x.account_pk)

            account_data[x.bank_id] = {
                "data": x,
                "last_movement": last_movement,
                "get_movements": True if last_movement is None else False,
            }
    del accounts

    for transaction in valid_transactions:
        current_bank_id = transaction.account.id
        if account_data[current_bank_id]["get_movements"]:
            pass
        elif isinstance(account_data[current_bank_id]["last_movement"], FiatTransaction) and transaction.id == account_data[current_bank_id]["last_movement"].bank_id:  # type: ignore
            account_data[current_bank_id]["get_movements"] = True
            continue
        if account_data[current_bank_id]["get_movements"]:
            movements.append(
                FiatTransaction(
                    balance=transaction.balance,
                    account_fk=account_data[current_bank_id]["data"].account_pk,  # type: ignore
                    amount=transaction.amount,
                    date=transaction.started_date,
                    category=transaction.category,
                    subcategory=transaction.tag,
                    name=transaction.merchant.name if transaction.merchant is not None else transaction.comment,
                    concept=transaction.description,
                    bank_id=transaction.id,
                )
            )
    return movements
