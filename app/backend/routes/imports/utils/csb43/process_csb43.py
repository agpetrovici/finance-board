import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO
from typing import Any, List

from csb43 import formats
from csb43.aeb43 import read_batch


@dataclass
class Summary:
    total_records: int
    padding: str


@dataclass
class OptionalItem:
    record_code: int
    item1: str
    item2: str


@dataclass
class Transaction:
    padding: str
    branch_code: str
    document_number: str
    transaction_date: date
    value_date: date
    shared_item: int
    own_item: int
    amount: Decimal
    reference1: str
    reference2: str
    optional_items: List[OptionalItem]


@dataclass
class AccountSummary:
    bank_code: str
    branch_code: str
    account_number: str
    expenses_entries: int
    expenses: Decimal
    income_entries: int
    income: Decimal
    final_balance: Decimal
    currency: str
    padding: str


@dataclass
class Account:
    bank_code: str
    branch_code: str
    account_number: str
    initial_date: date
    final_date: date
    initial_balance: Decimal
    currency: str
    information_mode: int
    short_name: str
    padding: str
    summary: AccountSummary
    transactions: List[Transaction]


@dataclass
class BankStatement:
    summary: Summary
    accounts: List[Account]


def parse_bank_statement(data: dict[str, Any]) -> BankStatement:
    """Parse a dictionary into a BankStatement object with proper type conversion."""

    def parse_date(date_str: str) -> date:
        return date.fromisoformat(date_str)

    def parse_decimal(amount_str: str) -> Decimal:
        return Decimal(amount_str)

    def parse_optional_items(items: List[dict[str, Any]]) -> List[OptionalItem]:
        return [OptionalItem(**item) for item in items]

    def parse_transaction(transaction: dict[str, Any]) -> Transaction:
        transaction_copy = transaction.copy()
        transaction_copy["transaction_date"] = parse_date(transaction["transaction_date"])
        transaction_copy["value_date"] = parse_date(transaction["value_date"])
        transaction_copy["amount"] = parse_decimal(transaction["amount"])
        transaction_copy["optional_items"] = parse_optional_items(transaction["optional_items"])
        return Transaction(**transaction_copy)

    def parse_account_summary(summary: dict[str, Any]) -> AccountSummary:
        summary_copy = summary.copy()
        summary_copy["expenses"] = parse_decimal(summary["expenses"])
        summary_copy["income"] = parse_decimal(summary["income"])
        summary_copy["final_balance"] = parse_decimal(summary["final_balance"])
        return AccountSummary(**summary_copy)

    def parse_account(account: dict[str, Any]) -> Account:
        account_copy = account.copy()
        account_copy["initial_date"] = parse_date(account["initial_date"])
        account_copy["final_date"] = parse_date(account["final_date"])
        account_copy["initial_balance"] = parse_decimal(account["initial_balance"])
        account_copy["summary"] = parse_account_summary(account["summary"])
        account_copy["transactions"] = [parse_transaction(t) for t in account["transactions"]]
        return Account(**account_copy)

    return BankStatement(summary=Summary(**data["summary"]), accounts=[parse_account(account) for account in data["accounts"]])


def parse_aes43(content: bytes | BytesIO) -> BankStatement:
    if isinstance(content, bytes):
        file_io = BytesIO(content)
    elif isinstance(content, BytesIO):
        file_io = content
    else:
        raise ValueError("Invalid file type")

    batch = read_batch(file_io)
    o = formats.convert_from_aeb43(batch, "json")
    data = json.loads(o.json)
    return parse_bank_statement(data)
