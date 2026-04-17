from fastapi import APIRouter, Request

from app.services import get_lead_dashboard_metrics

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def dashboard_page(request: Request):
    templates = request.app.state.templates
    metrics = get_lead_dashboard_metrics()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "page_title": "Dashboard",
            "total_leads": metrics["total_leads"],
            "status_counts": metrics["status_counts"],
        },
    )
