"""AI endpoints: CV tailoring."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.ai import TailorCvRequest, TailorCvResponse
from app.services.cv_tailoring import CvTailoringService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post(
    "/tailor-cv",
    response_model=TailorCvResponse,
    summary="Tailor a CV to a job description (optionally save as a new CV)",
)
def tailor_cv(data: TailorCvRequest, current_user: CurrentUser, db: DbSession) -> TailorCvResponse:
    return CvTailoringService(db).tailor(current_user, data)
