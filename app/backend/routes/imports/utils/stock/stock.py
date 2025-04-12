from bs4 import BeautifulSoup
from datetime import datetime
from decimal import Decimal

from app.backend.models.db import db
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.m_currency import Currency
from app.backend.models.m_execution_venue import ExecutionVenue
from app.backend.models.m_isin import Isin
from app.backend.models.m_reference_exchange import ReferenceExchange
from app.backend.models.m_stock_account import StockAccount

SPANISH_MONTHS = {
    "ene": "01",
    "feb": "02",
    "mar": "03",
    "abr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "ago": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dic": "12",
}

# TODOL: Should be linked to m_order_class
ORDER_CLASS_MAP = {
    "compra": 1,
    "venta": 2,
}

ORDER_TYPE_MAP = {
    "orden a mercado": 1,
    "otro": 2,
}


def parse_stock_data(text: str, stock_account: StockAccount) -> list[StockTransaction]:
    # Extract data from table
    soup = BeautifulSoup(text, "html.parser")
    table = soup.find("table", {"width": "580"})
    if not table:
        return []
    rows = table.find_all("tr")
    data = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) != 2:
            continue
        label = cells[0].get_text(strip=True).replace(":", "")
        value = cells[1].get_text(strip=True)
        data[label.lower()] = value

    # Map values
    order_id = data.get("id de la orden", "")

    date_str = data.get("fecha de ejecución", "")
    for spanish, month in SPANISH_MONTHS.items():
        date_str = date_str.replace(spanish, month)
    execution_date = datetime.strptime(date_str, "%d %m %Y, %H:%M:%S")

    fk_order_class = ORDER_CLASS_MAP[data.get("orden", "").lower()]
    fk_order_type = ORDER_TYPE_MAP[data.get("tipo", "").lower()]

    quantity = int(data.get("número", "0"))

    # Extract price and currency from "precio"
    price_str = data.get("precio", "")
    price_per_share_currency = "".join(c for c in price_str if c.isalpha())
    price_per_share_value = Decimal(price_str.replace(price_per_share_currency, "").replace(",", ".").strip())

    # Extract value and currency from "valor local"
    value_broker_str = data.get("valor local", "")
    value_broker_currency = "".join(c for c in value_broker_str if c.isalpha())
    value_broker = Decimal(value_broker_str.replace(value_broker_currency, "").replace(",", ".").strip())

    fx_rate = Decimal(data.get("tipo de cambio", "").replace(",", ".").strip())

    # Extract value and currency from "valor"
    value_user_str = data.get("valor", "")
    value_user_currency = "".join(c for c in value_user_str if c.isalpha())
    value_user = Decimal(value_user_str.replace(value_user_currency, "").replace(",", ".").strip())

    # Extract costs and currencies
    cost_autofx_str = data.get("costes autofx", "")
    cost_autofx_currency = "".join(c for c in cost_autofx_str if c.isalpha())
    cost_autofx_value = Decimal(cost_autofx_str.replace(cost_autofx_currency, "").replace(",", ".").strip())

    external_costs_str = data.get("costes de transacción y/o externos", "")
    external_costs_currency = "".join(c for c in external_costs_str if c.isalpha())
    external_costs_value = Decimal(external_costs_str.replace(external_costs_currency, "").replace(",", ".").strip())

    total_costs_str = data.get("costes totales", "")
    total_costs_currency = "".join(c for c in total_costs_str if c.isalpha())
    total_costs_value = Decimal(total_costs_str.replace(total_costs_currency, "").replace(",", ".").strip())

    # Extract total and currency
    total_str = data.get("total", "")
    total_user_currency = "".join(c for c in total_str if c.isalpha())
    total_user_value = Decimal(total_str.replace(total_user_currency, "").replace(",", ".").strip())

    ##### Add depending data
    # Check if currencies exist in database, if not create them
    currencies_to_check = {
        price_per_share_currency,
        value_broker_currency,
        value_user_currency,
        cost_autofx_currency,
        external_costs_currency,
        total_costs_currency,
        total_user_currency,
    }

    for currency_code in currencies_to_check:
        if currency_code:  # Skip empty strings
            currency = Currency.query.get(currency_code)
            if not currency:
                currency = Currency(code=currency_code, name=currency_code)
                db.session.add(currency)

    fk_isin = data.get("isin", "")
    fk_reference_exchange = data.get("bolsa de referencia", "")
    fk_execution_venue = data.get("centro de ejecución", "")
    # Check if the values exists, if not create it
    isin = Isin.query.get(fk_isin)
    if not isin:
        isin = Isin(pk_isin=fk_isin, name=fk_isin)
        db.session.add(isin)
    execution_venue = ExecutionVenue.query.get(fk_execution_venue)
    if not execution_venue:
        execution_venue = ExecutionVenue(pk_execution_venue=fk_execution_venue, name=fk_execution_venue)
        db.session.add(execution_venue)
    reference_exchange = ReferenceExchange.query.get(fk_reference_exchange)
    if not reference_exchange:
        reference_exchange = ReferenceExchange(pk_reference_exchange=fk_reference_exchange, name=fk_reference_exchange)
        db.session.add(reference_exchange)
    db.session.commit()

    # Create transaction
    transaction = StockTransaction(
        fk_stock_account=stock_account.account_pk,
        order_id=order_id,
        execution_date=execution_date,
        fk_isin=fk_isin,
        fk_order_type=fk_order_type,
        fk_order_class=fk_order_class,
        fk_reference_exchange=fk_reference_exchange,
        fk_execution_venue=fk_execution_venue,
        quantity=quantity,
        price_per_share_value=price_per_share_value,
        price_per_share_currency=price_per_share_currency,
        value_broker=value_broker,
        value_broker_currency=value_broker_currency,
        fx_rate=fx_rate,
        value_user=value_user,
        value_user_currency=value_user_currency,
        cost_autofx_value=cost_autofx_value,
        cost_autofx_currency=cost_autofx_currency,
        external_costs_value=external_costs_value,
        external_costs_currency=external_costs_currency,
        total_costs_value=total_costs_value,
        total_costs_currency=total_costs_currency,
        total_user_value=total_user_value,
        total_user_currency=total_user_currency,
    )

    return [transaction]
