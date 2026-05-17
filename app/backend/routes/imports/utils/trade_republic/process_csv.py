import csv
import io
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.backend.models.e_stock_cash_transfer import StockCashTransfer
from app.backend.models.e_stock_dividend import StockDividend
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.m_currency import Currency
from app.backend.models.m_isin import Isin
from app.backend.models.m_stock_account import StockAccount
from app.backend.models.stock.e_stock_symbol import StockSymbol

TRADING_TYPES = {"BUY", "SELL"}
DIVIDEND_TYPE = "DIVIDEND"
CASH_TRANSFER_TYPES = {
    "TRANSFER_INSTANT_INBOUND",
    "TRANSFER_INSTANT_OUTBOUND",
    "TRANSFER_INBOUND",
    "TRANSFER_OUTBOUND",
}

ORDER_CLASS_MAP = {
    "BUY": 1,
    "SELL": 2,
}

# Default to market order — TR CSV does not expose the order type
DEFAULT_ORDER_TYPE = 1


CsvRecord = StockTransaction | StockDividend | StockCashTransfer


@dataclass
class CsvImportResult:
    stock_transactions: list[StockTransaction] = field(default_factory=list)
    dividends: list[StockDividend] = field(default_factory=list)
    cash_transfers: list[StockCashTransfer] = field(default_factory=list)
    # All records in the original CSV row order, used to preserve insertion order.
    ordered: list[CsvRecord] = field(default_factory=list)

    def _append(self, record: CsvRecord) -> None:
        self.ordered.append(record)
        if isinstance(record, StockTransaction):
            self.stock_transactions.append(record)
        elif isinstance(record, StockDividend):
            self.dividends.append(record)
        elif isinstance(record, StockCashTransfer):
            self.cash_transfers.append(record)

    @property
    def total(self) -> int:
        return len(self.ordered)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_decimal(value: str, default: str = "0") -> Decimal:
    try:
        return Decimal(value.strip()) if value.strip() else Decimal(default)
    except InvalidOperation:
        return Decimal(default)


def _ensure_currency(session: Session, code: str) -> None:
    if not code:
        return
    if not session.get(Currency, code):
        session.add(Currency(code=code, name=code))


def _ensure_isin(session: Session, isin: str, name: str) -> None:
    if not session.get(Isin, isin):
        session.add(Isin(pk_isin=isin, name=name))


def _ensure_stock_symbol(session: Session, isin: str) -> StockSymbol:
    symbol = session.query(StockSymbol).filter_by(fk_isin=isin).first()
    if symbol:
        return symbol
    # ISINs are 12 chars; pk_symbol is capped at 10 — use truncated ISIN as fallback key
    symbol_key = isin[:10]
    symbol = session.get(StockSymbol, symbol_key)
    if not symbol:
        symbol = StockSymbol(pk_symbol=symbol_key, fk_isin=isin)
        session.add(symbol)
    return symbol


def _parse_dt(raw: str) -> datetime:
    return datetime.fromisoformat(raw.strip().replace("Z", "+00:00")).replace(tzinfo=None)


# ---------------------------------------------------------------------------
# Row processors
# ---------------------------------------------------------------------------

def _process_trading_row(
    session: Session,
    row: dict,
    stock_account: StockAccount,
) -> StockTransaction:
    tx_type = row["type"].strip()
    isin = row["symbol"].strip()
    asset_name = row.get("name", "").strip()
    currency = row.get("currency", "EUR").strip()
    original_currency = row.get("original_currency", "").strip()
    execution_date = _parse_dt(row["datetime"])

    _ensure_isin(session, isin, asset_name)
    stock_symbol = _ensure_stock_symbol(session, isin)
    _ensure_currency(session, currency)
    _ensure_currency(session, original_currency)
    session.flush()

    shares_raw = row.get("shares", "0")
    quantity = abs(int(float(shares_raw))) if shares_raw.strip() else 0

    price_per_share = _to_decimal(row.get("price", "0"))
    amount = _to_decimal(row.get("amount", "0"))
    fee = _to_decimal(row.get("fee", "0"))
    tax = _to_decimal(row.get("tax", "0"))
    fx_rate = _to_decimal(row.get("fx_rate", "1"), default="1") or Decimal("1")

    orig_amount_raw = row.get("original_amount", "").strip()
    has_fx = bool(original_currency and original_currency != currency)

    if has_fx and orig_amount_raw:
        value_broker = abs(_to_decimal(orig_amount_raw))
        value_broker_currency = original_currency
    else:
        value_broker = abs(amount)
        value_broker_currency = currency

    value_user = abs(amount)
    value_user_currency = currency
    external_costs_value = abs(fee)
    total_costs_value = abs(fee) + abs(tax)

    if tx_type == "BUY":
        total_user_value = value_user + total_costs_value
    else:
        total_user_value = value_user - total_costs_value

    return StockTransaction(
        fk_stock_account=stock_account.pk_stock_account,
        order_id=row.get("transaction_id", "").strip(),
        execution_date=execution_date,
        fk_isin=isin,
        fk_symbol=stock_symbol.pk_symbol,
        fk_order_type=DEFAULT_ORDER_TYPE,
        fk_order_class=ORDER_CLASS_MAP[tx_type],
        quantity=quantity,
        price_per_share_value=price_per_share,
        price_per_share_currency=currency,
        value_broker=value_broker,
        value_broker_currency=value_broker_currency,
        fx_rate=fx_rate,
        value_user=value_user,
        value_user_currency=value_user_currency,
        cost_autofx_value=None,
        cost_autofx_currency=None,
        external_costs_value=external_costs_value,
        external_costs_currency=currency,
        total_costs_value=total_costs_value,
        total_costs_currency=currency,
        total_user_value=total_user_value,
        total_user_currency=value_user_currency,
    )


def _process_dividend_row(
    session: Session,
    row: dict,
    stock_account: StockAccount,
) -> StockDividend:
    isin = row["symbol"].strip()
    asset_name = row.get("name", "").strip()
    currency = row.get("currency", "EUR").strip()
    original_currency = row.get("original_currency", "").strip()

    _ensure_isin(session, isin, asset_name)
    _ensure_currency(session, currency)
    _ensure_currency(session, original_currency)
    session.flush()

    shares_raw = row.get("shares", "0")
    shares = float(shares_raw.strip()) if shares_raw.strip() else 0.0

    orig_amount_raw = row.get("original_amount", "").strip()
    fx_rate_raw = row.get("fx_rate", "").strip()

    return StockDividend(
        fk_stock_account=stock_account.pk_stock_account,
        transaction_id=row.get("transaction_id", "").strip(),
        execution_date=_parse_dt(row["datetime"]),
        fk_isin=isin,
        asset_name=asset_name,
        shares=shares,
        amount=_to_decimal(row.get("amount", "0")),
        currency=currency,
        original_amount=_to_decimal(orig_amount_raw) if orig_amount_raw else None,
        original_currency=original_currency or None,
        fx_rate=_to_decimal(fx_rate_raw) if fx_rate_raw else None,
        tax=_to_decimal(row.get("tax", "0")) if row.get("tax", "").strip() else None,
    )


def _process_cash_transfer_row(
    session: Session,
    row: dict,
    stock_account: StockAccount,
) -> StockCashTransfer:
    currency = row.get("currency", "EUR").strip()
    _ensure_currency(session, currency)
    session.flush()

    return StockCashTransfer(
        fk_stock_account=stock_account.pk_stock_account,
        transaction_id=row.get("transaction_id", "").strip(),
        execution_date=_parse_dt(row["datetime"]),
        transfer_type=row.get("type", "").strip(),
        amount=_to_decimal(row.get("amount", "0")),
        currency=currency,
        description=row.get("description", "").strip() or None,
        counterparty_name=row.get("counterparty_name", "").strip() or None,
        counterparty_iban=row.get("counterparty_iban", "").strip() or None,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def process_trade_republic_csv(
    session: Session,
    content: bytes,
    stock_account: StockAccount,
) -> CsvImportResult:
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    result = CsvImportResult()

    for row in reader:
        tx_type = row.get("type", "").strip()

        if tx_type in TRADING_TYPES:
            result._append(_process_trading_row(session, row, stock_account))

        elif tx_type == DIVIDEND_TYPE:
            result._append(_process_dividend_row(session, row, stock_account))

        elif tx_type in CASH_TRANSFER_TYPES:
            result._append(_process_cash_transfer_row(session, row, stock_account))

    return result
