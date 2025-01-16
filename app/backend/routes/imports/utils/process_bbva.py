from datetime import datetime
from typing import Any, Optional

from app.backend.models.transaction import Transaction
from app.backend.routes.imports.utils.get_last_movement import get_last_movement


def get_new_movements(data: dict[str, Any], last_movement: Optional[Transaction], account_pk: int) -> list[Transaction]:
    movements = []
    get_movements = False
    if last_movement is None:
        get_movements = True
    for transaction in data["accountTransactions"][::-1]:
        if get_movements:
            pass
        elif isinstance(last_movement, Transaction) and transaction["id"] == last_movement.bank_id:
            get_movements = True
            continue
        if get_movements:
            movements.append(
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
    return movements


def process_bbva(account_pk: int, data: dict[str, Any]) -> None:
    last_bank_id = get_last_movement(account_pk)
    if last_bank_id is None:
        return None
    new_movements = get_new_movements(data, last_bank_id, account_pk)
    print(new_movements)
    return None
