from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from starlette import status

from app.services import (
    CandidateImportError,
    CandidateNotFoundError,
    CandidateStateError,
    convert_candidate_to_lead,
    import_candidates_from_csv,
    list_candidates,
    reject_candidate,
)

router = APIRouter(prefix="/candidates", tags=["Candidate queue"])


def _render_candidates_list(request: Request, error_message: str = ""):
    templates = request.app.state.templates
    return templates.TemplateResponse(
        request=request,
        name="candidates_list.html",
        context={
            "page_title": "Очередь кандидатов",
            "candidates": list_candidates(),
            "error_message": error_message,
        },
    )


@router.get("")
def candidates_list_page(request: Request):
    return _render_candidates_list(request=request)


@router.post("/import")
async def candidates_import_action(request: Request):
    form = await request.form()
    csv_text = str(form.get("csv_text", ""))

    try:
        imported = import_candidates_from_csv(csv_text)
    except CandidateImportError as error:
        return _render_candidates_list(request=request, error_message=str(error))

    if imported == 0:
        return _render_candidates_list(
            request=request,
            error_message="Нет строк для импорта: пустой ввод, только заголовок или только пустые строки.",
        )

    return RedirectResponse(
        url="/candidates",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{candidate_id}/reject")
async def candidate_reject_action(request: Request, candidate_id: int):
    try:
        reject_candidate(candidate_id)
    except CandidateNotFoundError as error:
        return _render_candidates_list(request=request, error_message=str(error))
    except CandidateStateError as error:
        return _render_candidates_list(request=request, error_message=str(error))

    return RedirectResponse(
        url="/candidates",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{candidate_id}/convert")
async def candidate_convert_action(request: Request, candidate_id: int):
    try:
        lead_id = convert_candidate_to_lead(candidate_id)
    except CandidateNotFoundError as error:
        return _render_candidates_list(request=request, error_message=str(error))
    except CandidateStateError as error:
        return _render_candidates_list(request=request, error_message=str(error))

    return RedirectResponse(
        url=f"/leads/{lead_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
