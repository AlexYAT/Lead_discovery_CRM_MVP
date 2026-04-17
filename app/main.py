from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes.base import router as base_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Lead Discovery CRM MVP")

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(base_router)


@app.get("/", tags=["SSR"])
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Lead Discovery CRM MVP"},
    )
