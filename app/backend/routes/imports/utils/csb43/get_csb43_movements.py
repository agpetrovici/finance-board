from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.backend.models.m_account import Account
from app.backend.models.e_transaction import FiatTransaction
from app.backend.routes.imports.utils.csb43.process_csb43 import BankStatement
from app.backend.routes.imports.utils.csb43.process_csb43 import Transaction as TransactionCsb43
from app.backend.routes.imports.utils.get_last_movement import get_last_movement


def get_new_movements(data: List[TransactionCsb43], last_transaction: Optional[FiatTransaction], account_pk: int) -> list[FiatTransaction]:
    movements = []
    balance = last_transaction.balance

    # If we managed to get here, is because we have a valid account in the database,
    # so if that is the case and we dont have a last_transaction, then
    # we have to get all the movements
    get_movements: bool = True if last_transaction is None else False

    for transaction in data:
        if get_movements:
            balance += transaction.amount
            movements.append(
                FiatTransaction(
                    balance=balance,
                    account_fk=account_pk,
                    amount=transaction.amount,
                    date=transaction.value_date,
                    category=None,
                    subcategory=None,
                    name=transaction.optional_items[0].item1,
                    concept=transaction.optional_items[0].item2,
                    bank_id=transaction.reference1,
                )
            )
        elif isinstance(last_transaction, FiatTransaction) and (transaction.reference1 == last_transaction.bank_id):
            get_movements = True
            continue

    return movements


def get_new_movements_from_BankStatement(session: Session, data: BankStatement) -> Tuple[bool, List[str], List[FiatTransaction]]:
    movements: List[FiatTransaction] = []
    status: bool = True
    messages: List[str] = []

    for account in data.accounts:
        # Given an account from the csb43 file, find the corresponding account in the database
        account_db: Account = (
            session.query(Account)
            .filter_by(
                bank_code=account.bank_code,
                branch_code=account.branch_code,
                account_number=account.account_number,
            )
            .first()
        )

        if account_db is None:
            status = False
            messages.append(f"Account {account.bank_code} {account.branch_code} {account.account_number} not found in the database")
            continue

        # After finding the account, find the last transaction saved in the database
        last_movement = get_last_movement(session, account_db.account_pk)

        # After finding the last movement, then make a list of new Transactions
        movements.extend(get_new_movements(account.transactions, last_movement, account_db.account_pk))

    return status, messages, movements
