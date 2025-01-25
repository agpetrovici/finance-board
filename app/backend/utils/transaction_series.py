from dataclasses import dataclass
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from decimal import Decimal
from typing import Dict, List, Set, Tuple

from app.backend.models.e_transaction import Transaction


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


def get_transaction_series() -> Tuple[List[Category], List[str]]:
    series: List[Category] = []
    dates: List[str] = []

    transactions = Transaction.query.filter(Transaction.date >= datetime.now().replace(year=datetime.now().year - 1)).all()
    if not transactions:
        return series, dates

    # Group transactions by date and category/subcategory
    categories_set: Set[str] = set()
    subcategories_set: Set[str] = set()
    transaction_groups: Dict[str, Dict[str, Dict[str, List[Transaction]]]] = {}

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

        series.append(Category(category=category, data=subcategories_data))

    return series, dates_sorted


def test_get_transaction_series() -> Tuple[List[Category], List[str]]:
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

    return series, categories
