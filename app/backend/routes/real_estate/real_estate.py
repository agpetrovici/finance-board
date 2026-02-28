from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.real_estate.e_real_estate_land_plot import RealEstateLandPlot

router = APIRouter(prefix="/real-estate", tags=["real_estate"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


@router.get("/", response_class=HTMLResponse)
def real_estate_index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "real_estate/real_estate.html")


@router.get("/api/properties", response_class=JSONResponse)
def real_estate_properties(session: Session = Depends(get_db)) -> JSONResponse:
    properties = session.query(RealEstateLandPlot).all()
    return JSONResponse(content=[p.to_dict() for p in properties])
