from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
