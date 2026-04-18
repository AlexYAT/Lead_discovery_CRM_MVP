from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.crm_service import (
    create_consultation,
    create_contact_attempt,
    get_consultation,
    list_consultations,
    list_contact_attempts,
    update_consultation_status,
)
from app.services.lead_service import get_lead

router = APIRouter(prefix="/api", tags=["CRM API"])


class ContactAttemptCreate(BaseModel):
    date: str = Field(default="", description="ISO or app date string; empty uses DB default")
    message_text: str | None = None
    outcome: str | None = None
    next_action: str | None = None


class ConsultationCreate(BaseModel):
    planned_at: str = ""
    status: str = "planned"
    result: str | None = None


class ConsultationPatch(BaseModel):
    status: str
    result: str | None = None


def _require_lead(lead_id: int) -> None:
    if get_lead(lead_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found",
        )


@router.post(
    "/leads/{lead_id}/contact",
    status_code=status.HTTP_201_CREATED,
)
def api_create_contact_attempt(lead_id: int, body: ContactAttemptCreate) -> dict[str, int]:
    _require_lead(lead_id)
    new_id = create_contact_attempt(
        lead_id=lead_id,
        date=body.date,
        message_text=body.message_text,
        outcome=body.outcome,
        next_action=body.next_action,
    )
    return {"id": new_id}


@router.get("/leads/{lead_id}/contacts")
def api_list_contact_attempts(lead_id: int) -> list[dict]:
    _require_lead(lead_id)
    return list_contact_attempts(lead_id=lead_id)


@router.post(
    "/leads/{lead_id}/consultations",
    status_code=status.HTTP_201_CREATED,
)
def api_create_consultation(lead_id: int, body: ConsultationCreate) -> dict[str, int]:
    _require_lead(lead_id)
    new_id = create_consultation(
        lead_id=lead_id,
        planned_at=body.planned_at,
        status=body.status,
        result=body.result,
    )
    return {"id": new_id}


@router.get("/leads/{lead_id}/consultations")
def api_list_consultations(lead_id: int) -> list[dict]:
    _require_lead(lead_id)
    return list_consultations(lead_id=lead_id)


@router.patch("/consultations/{consultation_id}")
def api_patch_consultation(
    consultation_id: int,
    body: ConsultationPatch,
) -> dict[str, str]:
    row = get_consultation(consultation_id=consultation_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found",
        )
    try:
        update_consultation_status(
            consultation_id=consultation_id,
            status=body.status,
            result=body.result,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
    return {"status": "ok"}
