from datetime import datetime
from typing import Any

from app.backend.models.transaction import Transaction
from app.backend.routes.imports.utils.get_last_movement import get_last_movement


def get_new_movements(data: dict[str, Any], last_bank_id: str, account_pk: int) -> list[Transaction]:
    values = []
    log_variables = False
    last_ix = 0
    for transaction in data["accountTransactions"][::-1]:
        if log_variables:
            last_ix += 1
            pass
        elif transaction["id"] == last_bank_id:
            log_variables = True
            continue
        if log_variables:
            values.append(
                Transaction(
                    balance=transaction["balance"]["accountingBalance"]["amount"],
                    account_fk=account_pk,
                    amount=transaction["amount"]["amount"],
                    date=datetime.fromisoformat(transaction["valueDate"]).date(),
                    category=transaction["humanCategory"].get("name", transaction["humanSubcategory"]["name"]),
                    subcategory=transaction["humanSubcategory"]["name"],
                    name=transaction.get("name", transaction["concept"]["name"]),
                    concept=transaction["humanExtendedConceptName"],
                    bank_id=transaction["id"],
                )
            )
    return values


def process_bbva(account_pk: int, data: dict[str, Any]) -> None:
    last_bank_id = get_last_movement(account_pk)
    if last_bank_id is None:
        return None
    new_movements = get_new_movements(data, last_bank_id, account_pk)
    print(new_movements)
    return None
