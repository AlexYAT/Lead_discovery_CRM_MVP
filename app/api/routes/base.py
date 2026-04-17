from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "lead-discovery-crm-mvp"}
