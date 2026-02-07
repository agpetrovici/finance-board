import json
from datetime import datetime
from decimal import Decimal
from os import getenv
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from mindee import ClientV2
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.e_transaction import FiatTransaction
from app.backend.models.m_account import Account
from app.backend.models.m_stock_account import StockAccount
from app.backend.routes.imports.utils.bankinter.process_bankinter import process_bankinter
from app.backend.routes.imports.utils.bbva.process_bbva import get_new_movements_bbva
from app.backend.routes.imports.utils.binance.get_account_balance import get_account_balance
from app.backend.routes.imports.utils.csb43.get_csb43_movements import get_new_movements_from_BankStatement
from app.backend.routes.imports.utils.csb43.process_csb43 import parse_aes43
from app.backend.routes.imports.utils.get_last_movement import get_last_movement
from app.backend.routes.imports.utils.imagin.process_imagin import process_imagin
from app.backend.routes.imports.utils.mindee_utils import polygon_to_bbox
from app.backend.routes.imports.utils.revolut.process_revolut import get_new_movements_revolut
from app.backend.routes.imports.utils.stock.stock import parse_stock_data
from app.backend.utils.receipts.prediction import make_receipt_prediction
from app.backend.utils.receipts.transaction import get_transaction
from app.backend.utils.receipts.utils import save_image, save_result

router = APIRouter(prefix="/imports", tags=["imports"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


@router.get("/", response_class=HTMLResponse)
def imports_index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_import_index.html")


@router.get("/bbva", response_class=HTMLResponse)
def import_bbva(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    accounts = session.query(Account).all()
    return templates.TemplateResponse(request, "imports/tpl_bbva.html", {"accounts": accounts})


@router.post("/from-bbva")
async def import_bbva_process(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    account_pk = data.get("accountPk")
    text = data.get("text")

    if account_pk == "" or text == "":
        return {"status": "error", "message": "No account pk or text provided."}

    try:
        account_pk = int(account_pk)
    except ValueError:
        return {"status": "error", "message": "Invalid account pk."}

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}

    # First get the last movement in the database so I know from where to get the data from the dict
    last_movement = get_last_movement(session, account_pk)
    if last_movement is None:
        return {"status": "error", "message": "No last bank id."}

    # Then get the new movements from the dict
    new_movements = get_new_movements_bbva(data, last_movement, account_pk)
    if not new_movements:
        return {"status": "error", "message": "No new movements."}

    # Then save the new movements to the database
    session.add_all(new_movements)
    session.commit()
    return {"status": "success", "message": f"Added {len(new_movements)} movements."}


@router.get("/bankinter", response_class=HTMLResponse)
def import_bankinter(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_bankinter.html")


@router.post("/from-bankinter")
async def import_bankinter_process(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    file = data.get("file")
    # Get the file content as binary to create the dataframe
    if file is None:
        return {"status": "error", "message": "No file provided."}

    try:
        import base64
        import io

        file_bytes = base64.b64decode(file)
        file_buffer = io.BytesIO(file_bytes)
    except Exception as e:
        return {"status": "error", "message": f"Could not process file: {str(e)}"}

    # Then get the new movements from the excel file
    new_movements = process_bankinter(session, file_buffer)
    if not new_movements:
        return {"status": "error", "message": "No new movements."}

    # Then save the new movements to the database
    session.add_all(new_movements)
    session.commit()
    return {"status": "success", "message": f"Added {len(new_movements)} movements."}


@router.get("/imagin", response_class=HTMLResponse)
def import_imagin(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_imagin.html")


@router.post("/from-imagin")
async def import_imagin_process(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    file = data.get("file")
    # Get the file content as binary to create the dataframe
    if file is None:
        return {"status": "error", "message": "No file provided."}

    try:
        import base64
        import io

        file_bytes = base64.b64decode(file)
        file_buffer = io.BytesIO(file_bytes)
    except Exception as e:
        return {"status": "error", "message": f"Could not process file: {str(e)}"}

    # Then get the new movements from the excel file
    new_movements = process_imagin(session, file_buffer)
    if not new_movements:
        return {"status": "error", "message": "No new movements."}

    # Then save the new movements to the database
    session.add_all(new_movements)
    session.commit()
    return {"status": "success", "message": f"Added {len(new_movements)} movements."}


@router.post("/test-from-bbva")
async def test_import_bbva_process(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    account_pk = data.get("accountPk")
    text = data.get("text")

    if account_pk == "" or text == "":
        return {"status": "error", "message": "No account pk or text provided."}

    try:
        account_pk = int(account_pk)
    except ValueError:
        return {"status": "error", "message": "Invalid account pk."}

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}

    # First get the last movement in the database so I know from where to get the data from the dict
    last_bank_id = get_last_movement(session, account_pk)
    if last_bank_id is None:
        return {"status": "error", "message": "No last bank id."}

    # Then get the new movements from the dict
    new_movements = get_new_movements_bbva(data, last_bank_id, account_pk)
    if not new_movements:
        return {"status": "error", "message": "No new movements."}

    return {"status": "success", "message": f"Added {len(new_movements)} movements."}


@router.get("/norma43", response_class=HTMLResponse)
def import_norma43(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_norma43.html")


@router.post("/from-norma43")
async def import_norma43_process(receipt: UploadFile, session: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        file_content: bytes = await receipt.read()
        bank_statement = parse_aes43(file_content)
    except Exception:
        return {"status": "error", "message": "Invalid file format."}

    status, messages, new_movements = get_new_movements_from_BankStatement(session, bank_statement)

    if status:
        # Then save the new movements to the database
        session.add_all(new_movements)
        session.commit()
        messages.append(f"Added {len(new_movements)} movements in the db.")
        return {"status": "success", "messages": messages}
    else:
        return {"status": "error", "messages": messages}


@router.get("/binance", response_class=HTMLResponse)
def import_binance(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_binance.html")


@router.post("/from-binance")
def import_from_binance(session: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        get_account_balance(session)
        return {"status": "success", "message": "Account balance imported successfully."}
    except Exception as e:
        return {"status": "error", "message": f"Account balance import failed: {e}."}


@router.get("/revolut", response_class=HTMLResponse)
def import_revolut(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/tpl_revolut.html")


@router.post("/from-revolut")
async def import_from_revolut(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    text = data.get("text")

    if text == "":
        return {"status": "error", "message": "No account pk or text provided."}

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON format."}

    accounts = session.query(Account).all()

    # Then get the new movements from the dict
    new_movements = get_new_movements_revolut(data, accounts)
    if not new_movements:
        return {"status": "error", "message": "No new movements."}

    # Then save the new movements to the database
    session.add_all(new_movements)
    session.commit()
    return {"status": "success", "message": f"Added {len(new_movements)} movements."}


@router.get("/receipts", response_class=HTMLResponse)
def import_receipts(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "imports/receipts/tpl_receipts.html")


@router.post("/get-receipt-data")
async def import_from_receipts(receipt: UploadFile, session: Session = Depends(get_db)) -> dict[str, Any]:
    data_input: bytes = await receipt.read()
    file_name = receipt.filename

    # Init a new client
    mindee_api_key = getenv("MINDEE_API_KEY")
    model_id = getenv("MINDEE_MODEL_ID")
    mindee_client = ClientV2(api_key=mindee_api_key)

    # Save the receipt image
    receipts_dir = Path(__file__).parent.parent.parent / "instance" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)

    fields = make_receipt_prediction(model_id, mindee_client, data_input, file_name)

    # Save the receipt image and the result for later debugging
    save_image(receipts_dir, data_input, file_name)
    save_result(receipts_dir, fields, file_name)

    _date = fields["date"].value
    _amount = fields["total_amount"].value
    if isinstance(_date, str):
        _date = datetime.strptime(_date, "%Y-%m-%d").date()
    if isinstance(_amount, float):
        _amount = -Decimal(str(_amount))

    transaction = get_transaction(session, _date, _amount)

    # Return the image file encoded in base64 within a JSON response
    data: dict[str, Any] = {}
    if file_name and data_input:
        data["transaction_pk"] = transaction.transaction_pk
        data["transaction"] = {
            # Data to be updated by the user
            "time": {
                "value": fields["time"].value,
                "bbox": polygon_to_bbox(fields["time"].locations[0].polygon),
            },
            "line_items": [
                {
                    "value": item.fields["description"].value,
                    "bbox": polygon_to_bbox(item.fields["total_price"].locations[0].polygon),
                }
                for item in fields["line_items"].object_items
            ],
            # For validation
            "date": {
                "value": fields["date"].value,
                "bbox": polygon_to_bbox(fields["date"].locations[0].polygon),
            },
            "total_amount": {
                "value": fields["total_amount"].value,
                "bbox": polygon_to_bbox(fields["total_amount"].locations[0].polygon),
            },
        }

    return {
        "status": "success",
        "message": "Image processed successfully",
        "data": data,
    }


@router.post("/update-receipt")
async def update_receipt(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    transaction_pk = data.get("transaction_pk")
    if not transaction_pk:
        return {"status": "error", "message": "No transaction pk provided."}

    # Find receipt in db
    receipt: FiatTransaction = session.query(FiatTransaction).filter_by(transaction_pk=transaction_pk).first()
    if receipt is None:
        return {"status": "error", "message": "Receipt not found."}

    # Clean the data to be updated
    _time: str = data.get("time")
    _date: datetime = receipt.date
    if _time:
        try:
            time_parts = _time.split(":")
            _date = _date.replace(hour=int(time_parts[0]), minute=int(time_parts[1]))
            if len(time_parts) > 2:  # Check if seconds are provided
                _date = _date.replace(second=int(time_parts[2]))
        except (ValueError, IndexError):
            pass

    receipt.date = _date
    receipt.description = "\n".join([x for x in data.get("line_items") if x != ""])

    # Update the receipt
    session.commit()

    return {"status": "success", "message": "Receipt updated successfully."}


@router.get("/stock", response_class=HTMLResponse)
def import_stock(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    accounts = session.query(StockAccount).all()
    return templates.TemplateResponse(request, "imports/tpl_stock.html", {"accounts": accounts})


@router.post("/from-stock")
async def import_from_stock(request: Request, session: Session = Depends(get_db)) -> dict[str, Any]:
    data = await request.json()
    if data is None:
        return {"status": "error", "message": "No data received."}

    text = data.get("text")
    account_pk = data.get("accountPk")
    if not text or not account_pk:
        return {"status": "error", "message": "No HTML content provided."}

    # Get stock account
    stock_account = session.query(StockAccount).filter_by(account_pk=account_pk).first()
    if stock_account is None:
        return {"status": "error", "message": "Stock account not found."}
    try:
        new_stock_data = parse_stock_data(session, text, stock_account)
        # Check if transactions already exist
        for transaction in new_stock_data:
            existing = (
                session.query(StockTransaction)
                .filter_by(fk_stock_account=transaction.fk_stock_account, order_id=transaction.order_id, execution_date=transaction.execution_date)
                .first()
            )

            if existing:
                return {"status": "error", "message": f"Transaction with order ID {transaction.order_id} already exists"}

        # Save to database
        session.add_all(new_stock_data)
        session.commit()
        return {"status": "success", "message": f"Successfully imported {len(new_stock_data)} stock records."}

    except Exception as e:
        session.rollback()
        return {"status": "error", "message": f"Error processing stock data: {str(e)}"}
