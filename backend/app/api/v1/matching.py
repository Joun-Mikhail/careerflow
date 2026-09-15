"""Match endpoints: score a CV against jobs."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.matching import MatchRequest, MatchResponse
from app.services.match_scoring import MatchScoringService

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post(
    "/score",
    response_model=MatchResponse,
    summary="Score a CV against one or more jobs",
)
def score_match(data: MatchRequest, current_user: CurrentUser, db: DbSession) -> MatchResponse:
    return MatchScoringService(db).score(current_user, data)
