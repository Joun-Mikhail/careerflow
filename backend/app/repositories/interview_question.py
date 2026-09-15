"""Interview question repository — user-scoped persistence and querying."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, or_

from app.models.interview_question import InterviewQuestion
from app.repositories.base import BaseRepository


class InterviewQuestionRepository(BaseRepository[InterviewQuestion]):
    """Data access for :class:`InterviewQuestion`."""

    model = InterviewQuestion

    def list_for_user(
        self,
        owner_id: UUID,
        *,
        tag: str | None = None,
        application_id: UUID | None = None,
    ) -> list[InterviewQuestion]:
        """Newest first, optionally narrowed to a tag or an application."""
        stmt = self.owned_query(owner_id)
        if application_id is not None:
            stmt = stmt.where(InterviewQuestion.application_id == application_id)
        if tag:
            # Tags are a comma-separated string, so match the tag as a
            # substring of the lowered field. Padding both sides with commas
            # keeps "sql" from matching "graphql".
            padded = func.lower("," + func.coalesce(InterviewQuestion.tags, "") + ",")
            needle = f",{tag.strip().lower()},"
            stmt = stmt.where(
                or_(
                    padded.like(f"%{needle}%"),
                    # Tolerate the spaces people actually type after commas.
                    func.lower(
                        ","
                        + func.replace(func.coalesce(InterviewQuestion.tags, ""), ", ", ",")
                        + ","
                    ).like(f"%{needle}%"),
                )
            )
        stmt = stmt.order_by(desc(InterviewQuestion.created_at))
        return list(self.session.execute(stmt).scalars())
