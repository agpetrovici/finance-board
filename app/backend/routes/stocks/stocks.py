from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from etl.etl_prices_portfolio import run as run_etl

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
    run_etl()
    return JSONResponse({"status": "done"})
