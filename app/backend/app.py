from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.backend.models.db import Base, engine
from app.backend.routes.api.api import router as router_api
from app.backend.routes.dashboard.dashboard import router as router_dashboard
from app.backend.routes.imports.imports import router as router_imports
from app.backend.routes.real_estate.real_estate import router as router_real_estate
from app.backend.routes.stocks.stocks import router as router_stocks


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Import all models so Base.metadata knows about them
    from app.backend.models.stock.e_stock_price import StockPriceDaily  # noqa: F401
    from app.backend.models.stock.e_stock_symbol import StockSymbol  # noqa: F401
    from app.backend.models.e_balance_crypto import BalanceCrypto  # noqa: F401
    from app.backend.models.e_deposit import Deposit  # noqa: F401
    from app.backend.models.e_invoice import Invoice  # noqa: F401
    from app.backend.models.e_stock_portfolio import StockPortfolio  # noqa: F401
    from app.backend.models.e_stock_transaction import StockTransaction  # noqa: F401
    from app.backend.models.e_transaction import FiatTransaction  # noqa: F401
    from app.backend.models.m_account import Account  # noqa: F401
    from app.backend.models.m_account_crypto import AccountCrypto  # noqa: F401
    from app.backend.models.m_client import Client  # noqa: F401
    from app.backend.models.m_currency import Currency  # noqa: F401
    from app.backend.models.m_execution_venue import ExecutionVenue  # noqa: F401
    from app.backend.models.m_isin import Isin  # noqa: F401
    from app.backend.models.m_order_class import OrderClass  # noqa: F401
    from app.backend.models.m_order_type import OrderType  # noqa: F401
    from app.backend.models.m_reference_exchange import ReferenceExchange  # noqa: F401
    from app.backend.models.m_stock_account import StockAccount  # noqa: F401
    from app.backend.models.real_estate.e_real_estate_land_plot import RealEstateLandPlot  # noqa: F401
    from app.backend.models.real_estate.e_real_estate_land_plot_comparable import RealEstateLandPlotComparable  # noqa: F401
    from app.backend.models.real_estate.e_real_estate_land_plot_comparable_geolocated import RealEstateLandPlotComparableGeolocated  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    # Mount static files for each blueprint-equivalent
    static_dir = Path(__file__).parent / "static"
    dashboard_static = Path(__file__).parent / "routes" / "dashboard" / "static"
    imports_static = Path(__file__).parent / "routes" / "imports" / "static"

    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    if dashboard_static.exists():
        app.mount("/dashboard/static", StaticFiles(directory=str(dashboard_static)), name="dashboard_static")
    if imports_static.exists():
        app.mount("/imports/static", StaticFiles(directory=str(imports_static)), name="imports_static")

    stocks_static = Path(__file__).parent / "routes" / "stocks" / "static"
    if stocks_static.exists():
        app.mount("/stocks/static", StaticFiles(directory=str(stocks_static)), name="stocks_static")

    real_estate_static = Path(__file__).parent / "routes" / "real_estate" / "static"
    if real_estate_static.exists():
        app.mount("/real-estate/static", StaticFiles(directory=str(real_estate_static)), name="real_estate_static")

    # Register routers
    app.include_router(router_api)
    app.include_router(router_dashboard)
    app.include_router(router_imports)
    app.include_router(router_stocks)
    app.include_router(router_real_estate)

    @app.get("/")
    def index() -> RedirectResponse:
        return RedirectResponse(url="/dashboard/")

    return app
