from dataclasses import dataclass
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
from typing import Dict, List, Set

from sqlalchemy.orm import Session

from app.backend.models.m_isin import Isin
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.e_transaction import FiatTransaction
from app.backend.routes.api.apex import ApexColumnChartData
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
    dates_sorted: List[str] = [date.strftime("%Y-%m-%d") for date in rrule(MONTHLY, dtstart=min_date, until=max_date)]

    # Create series grouped by category
    for category in categories_sorted:
        subcategories_data: List[Subcategory] = []
        for subcategory in subcategories_sorted:
            subcategory_data: List[DataPoint] = []
            for date in dates_sorted:
                # Sum amounts for each subcategory
                for _subcategory, txns in transaction_groups[date].get(category, {}).items():
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


def get_stock_transaction_series(session: Session) -> ApexColumnChartData:
    series: List[Category] = []
    dates: List[str] = []

    stock_transactions = session.query(StockTransaction).filter(StockTransaction.execution_date >= datetime.now().replace(year=datetime.now().year - 1)).all()
    if not stock_transactions:
        return ApexColumnChartData(series, dates)

    # Group transactions by date and category/subcategory
    categories_set: Set[str] = set()
    subcategories_set: Set[str] = set()
    transaction_groups: Dict[str, Dict[str, Dict[str, List[StockTransaction]]]] = {}

    transaction_dates: Set[datetime] = set()
    for t in stock_transactions:
        date_str = t.execution_date.replace(day=1).strftime("%Y-%m-%d")
        category = "stock"
        subcategory = t.fk_isin
        categories_set.add(category)
        subcategories_set.add(subcategory)
        transaction_dates.add(t.execution_date.replace(day=1))

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
    dates = [date.strftime("%Y-%m-%d") for date in rrule(MONTHLY, dtstart=min_date, until=max_date)]

    # Create series grouped by category
    for category in categories_sorted:
        subcategories_data: List[Subcategory] = []
        for subcategory in subcategories_sorted:
            isin = session.get(Isin, subcategory)
            subcategory_data: List[DataPoint] = []
            for date in dates:
                amount = Decimal("0")
                tooltips = []
                if date in transaction_groups and category in transaction_groups[date] and subcategory in transaction_groups[date][category]:
                    transactions = transaction_groups[date][category][subcategory]
                    amount = sum(t.quantity for t in transactions)
                    tooltips = [f"{isin.name}: {t.quantity}" for t in transactions]

                subcategory_data.append(DataPoint(x=date, y=amount, tooltip=tooltips))

            subcategories_data.append(Subcategory(name=isin.name, data=subcategory_data))

        series.append(Category(category=category, data=subcategories_data))

    return ApexColumnChartData(series, dates)
