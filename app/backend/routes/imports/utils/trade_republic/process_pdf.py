import io
import re
from datetime import datetime

import pdfplumber
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.m_stock_account import StockAccount
from app.backend.models.stock.e_stock_symbol import StockSymbol


async def process_pdf(pdf_file: UploadFile, session: Session) -> StockTransaction:
    content = await pdf_file.read()
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
    order_id = re.search(r"EJECUCIÓN ([\w\-]+)", text).group(1)
    # external_id = re.search(r"CUENTA DE VALORES (\d+)", text).group(1)
    iban = re.search(r"CUENTA DE EFECTIVO FECHA VALOR IMPORTE\n([\w\-]+)", text).group(1)

    day, month, year = re.search(r" FECHA (\d+)\.(\d+)\.(\d+)", text).group(1, 2, 3)
    hour, minute = re.search(r"LIQUIDACIÓN DE VALORES\nDESCRIPCIÓN\n.* a las (\d+):(\d+).*", text).group(1, 2)
    order_date = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute))

    fk_isin = re.search(r"ISIN: ([\w\-]+)", text).group(1)
    order_type_str = re.search(r"DESCRIPCIÓN\n(.*) .* a día", text).group(1)
    order_class_str = re.search(r"DESCRIPCIÓN\n.* (.*) a día", text).group(1)

    # Use a lazy quantifier .*? for the shortest match ending at ' en'
    stock_name = re.search(r"CUENTA DE EFECTIVO FECHA VALOR IMPORTE\n.*?\n(.*?) en", text).group(1)
    quantity = int(re.search(rf"POSICI[ÓO]N CANTIDAD PRECIO IMPORTE\n{re.escape(stock_name)} (\d+) [\d\.,]+ EUR", text).group(1))
    price_per_share_value = float(re.search(rf"POSICI[ÓO]N CANTIDAD PRECIO IMPORTE\n{re.escape(stock_name)} \d+ ([\d\.,]+) .*", text).group(1).replace(",", "."))
    price_per_share_currency = re.search(rf"POSICI[ÓO]N CANTIDAD PRECIO IMPORTE\n{re.escape(stock_name)} \d+ [\d\.,]+ (\w+)", text).group(1)

    # To capture -1,00 as a (possibly negative) float surrounded by optional spaces
    external_costs_value = float(re.search(r"Costes del servicio de ejecución de terceros\s+(-?\d+,\d+)", text).group(1).replace(",", "."))
    external_costs_currency = re.search(r"Costes del servicio de ejecución de terceros\s+-?\d+,\d+ (.*)", text).group(1)

    total_cost_value = float(re.search(r"POSICIÓN IMPORTE\nCostes del servicio de ejecución de terceros .*\nTOTAL (-?\d+,\d+)", text).group(1).replace(",", "."))
    total_cost_currency = re.search(r"POSICIÓN IMPORTE\nCostes del servicio de ejecución de terceros .*\nTOTAL -?\d+,\d+ (.*)", text).group(1)

    stock_symbol = session.query(StockSymbol).filter_by(fk_isin=fk_isin).first()
    if not stock_symbol:
        return {"status": "error", "message": f"Stock symbol with ISIN {fk_isin} not found"}

    match order_type_str:
        case "Market-Order":
            fk_order_type = 1  # MARKET

    match order_class_str:
        case "Comprar":
            fk_order_class = 1  # BUY
        case "Venta" | "Vender":
            fk_order_class = 2  # SELL

    stock_account = session.query(StockAccount).filter_by(iban=iban).first()
    if not stock_account:
        return {"status": "error", "message": f"Stock account with IBAN {iban} not found"}

    return StockTransaction(
        fk_stock_account=stock_account.pk_stock_account,
        order_id=order_id,
        execution_date=order_date,
        fk_isin=fk_isin,
        fk_order_type=fk_order_type,
        fk_order_class=fk_order_class,
        quantity=quantity,
        price_per_share_value=price_per_share_value,
        price_per_share_currency=price_per_share_currency,
        external_costs_value=external_costs_value,
        external_costs_currency=external_costs_currency,
        total_costs_value=external_costs_value,
        total_costs_currency=external_costs_currency,
        total_user_value=total_cost_value,
        total_user_currency=total_cost_currency,
        value_user=-total_cost_value,
        value_user_currency=total_cost_currency,
        value_broker=-total_cost_value,
        value_broker_currency=total_cost_currency,
        fk_symbol=stock_symbol.pk_symbol,
        fx_rate=1,
        cost_autofx_value=0,
        cost_autofx_currency=total_cost_currency,
    )
