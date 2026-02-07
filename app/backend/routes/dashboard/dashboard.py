from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

templates = Jinja2Templates(
    directory=[
        str(Path(__file__).parent / "templates"),
        str(Path(__file__).parent.parent.parent / "templates"),
    ]
)


@router.get("/", response_class=HTMLResponse)
def get_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "dashboard/dashboard.html")


@router.get("/test-dashboard", response_class=HTMLResponse)
def test_get_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "dashboard/test_dashboard.html")
