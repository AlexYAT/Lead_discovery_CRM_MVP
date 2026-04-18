from pathlib import Path

from app.core.env_init import initialize_environment

initialize_environment()

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.base import router as base_router
from app.api.routes.crm import router as crm_api_router
from app.db import init_db
from app.web import candidates_router, dashboard_router, leads_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Lead Discovery CRM MVP")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.state.templates = templates

app.include_router(base_router)
app.include_router(crm_api_router)
app.include_router(candidates_router)
app.include_router(leads_router)
app.include_router(dashboard_router)


@app.on_event("startup")
def startup_init_db():
    init_db()


@app.get("/", tags=["SSR"])
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_title": "Lead Discovery CRM MVP",
            "lead_crm_url": "/leads",
            "dashboard_url": "/dashboard",
            "candidates_url": "/candidates",
        },
    )
