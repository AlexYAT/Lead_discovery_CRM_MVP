from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from starlette import status

from app.services import (
    InvalidStatusTransitionError,
    LEAD_STATUSES,
    create_contact_attempt,
    create_lead,
    get_allowed_next_statuses,
    get_lead,
    list_contact_attempts_by_lead,
    list_leads,
    update_lead_notes,
    update_lead_status,
)

router = APIRouter(prefix="/leads", tags=["Lead CRM"])


def _render_leads_list(request: Request, error_message: str = ""):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="leads_list.html",
        context={
            "page_title": "Lead CRM",
            "leads": list_leads(),
            "statuses": LEAD_STATUSES,
            "error_message": error_message,
        },
    )


def _render_lead_detail(request: Request, lead_id: int, error_message: str = ""):
    lead = get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="lead_detail.html",
        context={
            "page_title": f"Lead #{lead_id}",
            "lead": lead,
            "allowed_next_statuses": get_allowed_next_statuses(str(lead["status"])),
            "contact_attempts": list_contact_attempts_by_lead(lead_id=lead_id),
            "error_message": error_message,
        },
    )


@router.get("")
def leads_list_page(request: Request):
    return _render_leads_list(request=request)


@router.post("")
async def lead_create_action(request: Request):
    form = await request.form()

    platform = str(form.get("platform", "")).strip()
    profile_name = str(form.get("profile_name", "")).strip()
    profile_url = str(form.get("profile_url", "")).strip()

    if not platform or not profile_name or not profile_url:
        return _render_leads_list(
            request=request,
            error_message="Заполните обязательные поля: platform, profile_name, profile_url.",
        )

    lead_id = create_lead(
        platform=platform,
        profile_name=profile_name,
        profile_url=profile_url,
        source_url=str(form.get("source_url", "")),
        source_text=str(form.get("source_text", "")),
        detected_theme=str(form.get("detected_theme", "")),
        score=str(form.get("score", "")),
        notes=str(form.get("notes", "")),
    )

    return RedirectResponse(
        url=f"/leads/{lead_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{lead_id}")
def lead_detail_page(request: Request, lead_id: int):
    return _render_lead_detail(request=request, lead_id=lead_id)


@router.post("/{lead_id}/status")
async def lead_status_update_action(request: Request, lead_id: int):
    form = await request.form()
    new_status = str(form.get("new_status", "")).strip()

    try:
        update_lead_status(lead_id=lead_id, new_status=new_status)
    except InvalidStatusTransitionError as error:
        return _render_lead_detail(
            request=request,
            lead_id=lead_id,
            error_message=f"Ошибка перехода статуса: {error}",
        )

    return RedirectResponse(
        url=f"/leads/{lead_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{lead_id}/notes")
async def lead_notes_update_action(request: Request, lead_id: int):
    form = await request.form()
    update_lead_notes(lead_id=lead_id, notes=str(form.get("notes", "")))

    return RedirectResponse(
        url=f"/leads/{lead_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{lead_id}/contacts")
async def lead_contact_add_action(request: Request, lead_id: int):
    form = await request.form()

    lead = get_lead(lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")

    create_contact_attempt(
        lead_id=lead_id,
        date=str(form.get("date", "")),
        message_text=str(form.get("message_text", "")),
        outcome=str(form.get("outcome", "")),
        next_action=str(form.get("next_action", "")),
    )

    return RedirectResponse(
        url=f"/leads/{lead_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
