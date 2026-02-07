import json
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.e_stock_transaction import StockTransaction
from app.backend.models.portfolio.portfolio import Portfolio
from app.backend.models.stock.e_stock_price import StockPriceDaily
from app.backend.utils.stock.calculate_portfolio import calculate_portfolio

router = APIRouter(prefix="/stocks", tags=["stocks"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


def _portfolio_to_series(portfolio: Portfolio) -> list[dict]:
    """Convert a Portfolio into ApexCharts-compatible series.

    Each Stock becomes a series whose data points are
    ``[timestamp_ms, value]`` pairs (value = quantity * close price).
    """
    series: list[dict] = []
    for stock in portfolio.stocks:
        data_points = [
            [int(sv.date.timestamp() * 1000), round(sv.value, 2)]
            for sv in stock.values
        ]
        series.append({"name": stock.symbol, "data": data_points})
    return series


@router.get("/", response_class=HTMLResponse)
def stocks_index(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    stock_transactions = session.query(StockTransaction).all()
    stock_prices = session.query(StockPriceDaily).order_by(StockPriceDaily.date.asc()).all()

    portfolio: Portfolio = calculate_portfolio(stock_transactions, stock_prices)
    series = _portfolio_to_series(portfolio)

    return templates.TemplateResponse(
        request,
        "stocks/stocks.html",
        {"series": json.dumps(series)},
    )
