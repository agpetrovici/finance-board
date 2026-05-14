import traceback
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.backend.utils.logger.operation_logger import get_logger
from etl.etl_prices_portfolio import run as run_etl

operation_logger = get_logger("update-prices")

router = APIRouter(prefix="/stocks", tags=["stocks"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


@router.get("/", response_class=HTMLResponse)
def stocks_index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "stocks/stocks.html")


@router.post("/update-prices", response_class=JSONResponse)
def update_prices() -> JSONResponse:
    try:
        run_etl()
        return JSONResponse({"status": "done"})
    except Exception as e:
        operation_logger.error(f"Error updating prices: {e}")
        operation_logger.error(traceback.format_exc())
        return JSONResponse(
            {
                "status": "error",
                "message": str(e),
            }
        )
