from dataclasses import dataclass
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.backend.models.m_isin import Isin
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.utils.stock.calculate_portfolio import ORDER_CLASS_BUY, ORDER_CLASS_SELL
from app.backend.models.e_transaction import FiatTransaction
from app.backend.routes.api.apex import (
    ApexColumnChartData,
    Category as IncExpCategory,
    IncomeAndExpensesStatement,
    Subcategory as IncExpSubcategory,
)
from app.backend.utils.bank_statement import get_deposits


@dataclass
class DataPoint:
    x: str
    y: Decimal
    tooltip: List[str]


@dataclass
class Subcategory:
    name: str
    data: List[DataPoint]


@dataclass
class Category:
    category: str
    data: List[Subcategory]


def get_transaction_series(session: Session) -> ApexColumnChartData:
    series: List[Category] = []
    dates: List[str] = []

    transactions = session.query(FiatTransaction).filter(FiatTransaction.date >= datetime.now().replace(year=datetime.now().year - 1)).all()
    if not transactions:
        return ApexColumnChartData(series, dates)

    deposits = get_deposits(session)
    for deposit in deposits:
        # TODOL Add category and subcategory in Deposit table
        transactions.append(FiatTransaction(date=deposit.date_start, name=deposit.name, category="Deposit", subcategory="Deposit", amount=deposit.amount))

    # Group transactions by date and category/subcategory
    categories_set: Set[str] = set()
    subcategories_set: Set[str] = set()
    transaction_groups: Dict[str, Dict[str, Dict[str, List[FiatTransaction]]]] = {}

    transaction_dates: Set[datetime] = set()
    for t in transactions:
        date_str = t.date.replace(day=1).strftime("%Y-%m-%d")
        category = t.category or "Uncategorized"
        subcategory = t.subcategory or "Uncategorized"
        categories_set.add(category)
        subcategories_set.add(subcategory)
        transaction_dates.add(t.date.replace(day=1))
        if date_str not in transaction_groups:
            transaction_groups[date_str] = {}

        if category not in transaction_groups[date_str]:
            transaction_groups[date_str][category] = {}

        if subcategory not in transaction_groups[date_str][category]:
            transaction_groups[date_str][category][subcategory] = []
        transaction_groups[date_str][category][subcategory].append(t)

    categories_sorted: List[str] = sorted(list(categories_set))
    subcategories_sorted: List[str] = sorted(list(subcategories_set))
    transaction_dates_sorted: List[datetime] = sorted(list(transaction_dates))
    min_date = min(transaction_dates_sorted)
    max_date = max(transaction_dates_sorted)
    # dates to plot
    dates_sorted: List[str] = [date.strftime("%Y-%m-%d") for date in rrule(MONTHLY, dtstart=min_date, until=max_date)]

    # Create series grouped by category
    for category in categories_sorted:
        subcategories_data: List[Subcategory] = []
        for subcategory in subcategories_sorted:
            subcategory_data: List[DataPoint] = []
            for date in dates_sorted:
                # Sum amounts for each subcategory (use .get() since not all dates have transactions)
                for _subcategory, txns in transaction_groups.get(date, {}).get(category, {}).items():
                    if _subcategory != subcategory:
                        # subcategory_data.append(DataPoint(x=date, y=Decimal("0"), tooltip=[""]))
                        continue
                    total = sum(t.amount for t in txns)
                    tooltips = [f"{t.date} {t.name}: {t.category} {t.subcategory} {t.amount}" for t in txns]
                    subcategory_data.append(DataPoint(x=date, y=total, tooltip=tooltips))
            if subcategory_data:
                subcategories_data.append(Subcategory(name=subcategory, data=subcategory_data))

        # Ensure all subcategories have data points for all dates
        for subcategory in subcategories_data:
            existing_dates = {dp.x for dp in subcategory.data}
            for date in dates_sorted:
                if date not in existing_dates:
                    subcategory.data.append(DataPoint(x=date, y=Decimal("0"), tooltip=[]))
            # Sort data points by date
            subcategory.data.sort(key=lambda dp: dp.x)
        series.append(Category(category=category, data=subcategories_data))

    return ApexColumnChartData(series, dates_sorted)


def test_get_transaction_series() -> ApexColumnChartData:
    categories = [
        "2023-01-01",
        "2023-02-01",
        "2023-03-01",
        "2023-04-01",
        "2023-05-01",
        "2023-06-01",
        "2023-71-10",
    ]

    series = [
        Category(
            category="PRODUCT A",
            data=[
                Subcategory(
                    name="PRODUCT A",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("11"), tooltip=["Element A - 1", "Element B - 5000", "Element C - 10000"]),
                        DataPoint(x="2023-02-01", y=Decimal("55"), tooltip=["Custom tooltip for A - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("41"), tooltip=["Custom tooltip for A - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("67"), tooltip=["Custom tooltip for A - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("22"), tooltip=["Custom tooltip for A - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("43"), tooltip=["Custom tooltip for A - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("36"), tooltip=["Custom tooltip for A - Jan 7"]),
                    ],
                ),
                Subcategory(
                    name="PRODUCT B",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("44"), tooltip=["Custom tooltip for A - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("55"), tooltip=["Custom tooltip for A - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("41"), tooltip=["Custom tooltip for A - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("67"), tooltip=["Custom tooltip for A - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("22"), tooltip=["Custom tooltip for A - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("43"), tooltip=["Custom tooltip for A - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("36"), tooltip=["Custom tooltip for A - Jan 7"]),
                    ],
                ),
            ],
        ),
        Category(
            category="PRODUCT B",
            data=[
                Subcategory(
                    name="PRODUCT 1",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("0"), tooltip=["Custom tooltip for 1 - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("55"), tooltip=["Custom tooltip for 1 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("41"), tooltip=["Custom tooltip for 1 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("67"), tooltip=["Custom tooltip for 1 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("22"), tooltip=["Custom tooltip for 1 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("43"), tooltip=["Custom tooltip for 1 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("36"), tooltip=["Custom tooltip for 1 - Jan 7"]),
                    ],
                ),
                Subcategory(
                    name="PRODUCT 2",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("13"), tooltip=["Custom tooltip for 2 - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("0"), tooltip=["Custom tooltip for 2 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("20"), tooltip=["Custom tooltip for 2 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("8"), tooltip=["Custom tooltip for 2 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("13"), tooltip=["Custom tooltip for 2 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("27"), tooltip=["Custom tooltip for 2 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("20"), tooltip=["Custom tooltip for 2 - Jan 7"]),
                    ],
                ),
                Subcategory(
                    name="PRODUCT 3",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("11"), tooltip=["Custom tooltip for 3 - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("17"), tooltip=["Custom tooltip for 3 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("0"), tooltip=["Custom tooltip for 3 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("15"), tooltip=["Custom tooltip for 3 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("21"), tooltip=["Custom tooltip for 3 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("14"), tooltip=["Custom tooltip for 3 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("18"), tooltip=["Custom tooltip for 3 - Jan 7", "Other tooltip"]),
                    ],
                ),
            ],
        ),
        Category(
            category="PRODUCT C",
            data=[
                Subcategory(
                    name="PRODUCT 1",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("0"), tooltip=["Custom tooltip for 1 - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("55"), tooltip=["Custom tooltip for 1 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("41"), tooltip=["Custom tooltip for 1 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("67"), tooltip=["Custom tooltip for 1 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("22"), tooltip=["Custom tooltip for 1 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("43"), tooltip=["Custom tooltip for 1 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("36"), tooltip=["Custom tooltip for 1 - Jan 7"]),
                    ],
                ),
                Subcategory(
                    name="PRODUCT 2",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("13"), tooltip=["Custom tooltip for 2 - Jan 1"]),
                        DataPoint(x="2023-02-01", y=Decimal("0"), tooltip=["Custom tooltip for 2 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("20"), tooltip=["Custom tooltip for 2 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("8"), tooltip=["Custom tooltip for 2 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("13"), tooltip=["Custom tooltip for 2 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("27"), tooltip=["Custom tooltip for 2 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("20"), tooltip=["Custom tooltip for 2 - Jan 7"]),
                    ],
                ),
                Subcategory(
                    name="PRODUCT 3",
                    data=[
                        DataPoint(x="2023-01-01", y=Decimal("11"), tooltip=["A", "B", "C"]),
                        DataPoint(x="2023-02-01", y=Decimal("17"), tooltip=["Custom tooltip for 3 - Jan 2"]),
                        DataPoint(x="2023-03-01", y=Decimal("0"), tooltip=["Custom tooltip for 3 - Jan 3"]),
                        DataPoint(x="2023-04-01", y=Decimal("15"), tooltip=["Custom tooltip for 3 - Jan 4"]),
                        DataPoint(x="2023-05-01", y=Decimal("21"), tooltip=["Custom tooltip for 3 - Jan 5"]),
                        DataPoint(x="2023-06-01", y=Decimal("14"), tooltip=["Custom tooltip for 3 - Jan 6"]),
                        DataPoint(x="2023-07-01", y=Decimal("18"), tooltip=["Custom tooltip for 3 - Jan 7", "Other tooltip"]),
                    ],
                ),
            ],
        ),
    ]

    return ApexColumnChartData(series, categories)


def _signed_stock_value(t: StockTransaction) -> Decimal:
    """Transaction value in user currency; BUY positive, SELL negative."""
    value = abs(Decimal(str(t.value_user)))
    if t.fk_order_class == ORDER_CLASS_SELL:
        return -value
    return value


def _stock_tx_tooltip(t: StockTransaction, isin_name: str) -> str:
    side = "BUY" if t.fk_order_class == ORDER_CLASS_BUY else "SELL"
    signed_value = _signed_stock_value(t)
    return (
        f"{t.execution_date.strftime('%Y-%m-%d')} {side} {isin_name}: "
        f"{t.quantity} × {t.price_per_share_value} {t.price_per_share_currency} = "
        f"{signed_value} {t.value_user_currency}"
    )


def get_stock_transaction_series(session: Session) -> ApexColumnChartData:
    series: List[Category] = []
    dates: List[str] = []

    stock_transactions = session.query(StockTransaction).filter(StockTransaction.execution_date >= datetime(datetime.now().year - 1, 1, 1)).all()
    if not stock_transactions:
        return ApexColumnChartData(series, dates)

    subcategories_set: Set[str] = set()
    transaction_groups: Dict[str, Dict[str, List[StockTransaction]]] = {}

    transaction_dates: Set[datetime] = set()
    for t in stock_transactions:
        month_start = t.execution_date.date().replace(day=1)
        date_str = month_start.strftime("%Y-%m-%d")
        subcategory = t.fk_isin
        subcategories_set.add(subcategory)
        transaction_dates.add(month_start)
        transaction_groups.setdefault(date_str, {}).setdefault(subcategory, []).append(t)

    isins_by_pk = {i.pk_isin: i for i in session.query(Isin).filter(Isin.pk_isin.in_(subcategories_set)).all()}

    subcategories_sorted: List[str] = sorted(subcategories_set)
    transaction_dates_sorted = sorted(transaction_dates)
    min_date = min(transaction_dates_sorted)
    max_date = max(transaction_dates_sorted)
    dates = [d.strftime("%Y-%m-%d") for d in rrule(MONTHLY, dtstart=min_date, until=max_date)]

    subcategories_data: List[Subcategory] = []
    for subcategory in subcategories_sorted:
        isin = isins_by_pk.get(subcategory)
        isin_name = isin.name if isin else subcategory
        subcategory_data: List[DataPoint] = []
        for date in dates:
            amount = Decimal("0")
            tooltips: List[str] = []
            txns = transaction_groups.get(date, {}).get(subcategory, [])
            if txns:
                amount = sum(_signed_stock_value(t) for t in txns)
                tooltips = [_stock_tx_tooltip(t, isin_name) for t in txns]

            subcategory_data.append(DataPoint(x=date, y=amount, tooltip=tooltips))

        if any(dp.y != Decimal("0") for dp in subcategory_data):
            subcategories_data.append(Subcategory(name=isin_name, data=subcategory_data))

    if subcategories_data:
        series.append(Category(category="", data=subcategories_data))

    return ApexColumnChartData(series, dates)


def get_income_expenses_statements(session: Session) -> List[IncomeAndExpensesStatement]:
    """Build per-month income / expense statements from fiat transactions.

    A category is classified as *income* when the sum of its subcategory
    amounts for that month is positive, and *expense* otherwise.
    """
    transactions = session.query(FiatTransaction).filter(FiatTransaction.date >= datetime.now().replace(year=datetime.now().year - 1)).all()
    if not transactions:
        return []

    monthly_data: Dict[str, Dict[str, Dict[str, float]]] = {}

    for t in transactions:
        month_str = t.date.replace(day=1).strftime("%Y-%m-%d")
        category = t.category or "Uncategorized"
        subcategory = t.subcategory or "Uncategorized"

        monthly_data.setdefault(month_str, {}).setdefault(category, {}).setdefault(subcategory, 0.0)
        monthly_data[month_str][category][subcategory] += float(t.amount)

    statements: List[IncomeAndExpensesStatement] = []
    for month_str in sorted(monthly_data.keys()):
        incomes: List[IncExpCategory] = []
        expenses: List[IncExpCategory] = []

        for cat_name, subcats in sorted(monthly_data[month_str].items()):
            cat_total = sum(subcats.values())
            subcategories = [IncExpSubcategory(name=sub_name, amount=round(amount, 2)) for sub_name, amount in sorted(subcats.items())]
            cat = IncExpCategory(name=cat_name, subcategories=subcategories)

            if cat_total > 0:
                incomes.append(cat)
            else:
                expenses.append(cat)

        statements.append(
            IncomeAndExpensesStatement(
                month=datetime.strptime(month_str, "%Y-%m-%d").date(),
                incomes=incomes,
                expenses=expenses,
            )
        )

    return statements
