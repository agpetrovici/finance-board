import math
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.backend.models.db import get_db
from app.backend.models.real_estate.e_real_estate_land_plot import RealEstateLandPlot
from app.backend.models.real_estate.e_real_estate_land_plot_comparable import RealEstateLandPlotComparable
from app.backend.models.real_estate.e_real_estate_land_plot_comparable_geolocated import RealEstateLandPlotComparableGeolocated


router = APIRouter(prefix="/real-estate", tags=["real_estate"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


def _build_economic_lookup(
    listings: list[RealEstateLandPlotComparable],
) -> dict[str, dict]:
    """Group listings by reference and average their economic fields."""
    groups: dict[str, list[RealEstateLandPlotComparable]] = {}
    for listing in listings:
        if listing.reference is not None:
            groups.setdefault(listing.reference, []).append(listing)

    lookup: dict[str, dict] = {}
    for ref, items in groups.items():
        prices = [i.price for i in items]
        prices_per_m2 = [i.price_per_square_meter for i in items]
        lookup[ref] = {
            "avg_price": round(sum(prices) / len(prices), 2),
            "avg_price_per_m2": round(sum(prices_per_m2) / len(prices_per_m2), 2),
            "listings_count": len(items),
            "listings": [{"url": i.url, "title": i.title} for i in items],
        }
    return lookup


def _serialize_comparables(
    geolocated: list[RealEstateLandPlotComparableGeolocated],
    economic_lookup: dict[str, dict],
) -> list[dict]:
    results = []
    for g in geolocated:
        if g.coordinates is None:
            continue
        entry: dict = {
            "reference": g.pk_reference20,
            "surface": g.surface,
            "address": g.address,
            "lat": g.coordinates.x,
            "lng": g.coordinates.y,
        }
        econ = economic_lookup.get(g.pk_reference20)
        if econ:
            entry.update(econ)
        results.append(entry)
    return results


@router.get("/", response_class=HTMLResponse)
def real_estate_index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "real_estate/real_estate.html")


@router.get("/api/properties", response_class=JSONResponse)
def real_estate_properties(session: Session = Depends(get_db)) -> JSONResponse:
    properties = session.query(RealEstateLandPlot).all()
    return JSONResponse(content=[p.to_dict() for p in properties])


@router.get("/api/comparables", response_class=JSONResponse)
def real_estate_comparables(session: Session = Depends(get_db)) -> JSONResponse:
    geolocated = session.query(RealEstateLandPlotComparableGeolocated).all()
    listings = (
        session.query(RealEstateLandPlotComparable)
        .filter(
            RealEstateLandPlotComparable.reference.isnot(None),
        )
        .all()
    )
    economic_lookup = _build_economic_lookup(listings)
    return JSONResponse(content=_serialize_comparables(geolocated, economic_lookup))


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_comparables_table(
    properties: list[RealEstateLandPlot],
    geolocated: list[RealEstateLandPlotComparableGeolocated],
    economic_lookup: dict[str, dict],
) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    property_prices: dict[str, list[float]] = {}

    for p in properties:
        if p.coordinates is None:
            continue
        for g in geolocated:
            if g.coordinates is None:
                continue
            distance = _haversine_km(p.coordinates.x, p.coordinates.y, g.coordinates.x, g.coordinates.y)
            if distance > 1:
                continue
            econ = economic_lookup.get(g.pk_reference20, {})
            ppm2 = econ.get("avg_price_per_m2")
            rows.append(
                {
                    "property_title": p.title,
                    "comparable_ref": g.pk_reference20,
                    "distance_km": round(distance, 2),
                    "price_per_m2": ppm2,
                    "surface": g.surface,
                }
            )
            if ppm2 is not None:
                property_prices.setdefault(p.title, []).append(ppm2)

    rows.sort(key=lambda r: r["distance_km"])

    market_prices: list[dict] = []
    for p in properties:
        ppm2_values = property_prices.get(p.title, [])
        if not ppm2_values:
            continue
        avg_ppm2 = sum(ppm2_values) / len(ppm2_values)
        market_prices.append(
            {
                "title": p.title,
                "surface": p.surface,
                "avg_price_per_m2": round(avg_ppm2, 2),
                "market_price": round(avg_ppm2 * p.surface, 2),
            }
        )

    return rows, market_prices


@router.get("/api/comparables-table", response_class=HTMLResponse)
def real_estate_comparables_table(request: Request, session: Session = Depends(get_db)) -> HTMLResponse:
    properties = session.query(RealEstateLandPlot).all()
    geolocated = session.query(RealEstateLandPlotComparableGeolocated).all()
    listings = (
        session.query(RealEstateLandPlotComparable)
        .filter(
            RealEstateLandPlotComparable.reference.isnot(None),
        )
        .all()
    )
    economic_lookup = _build_economic_lookup(listings)
    rows, market_prices = _build_comparables_table(properties, geolocated, economic_lookup)

    return templates.TemplateResponse(
        request,
        "real_estate/_comparables_table.html",
        {"rows": rows, "market_prices": market_prices},
    )
