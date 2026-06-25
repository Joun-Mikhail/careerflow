"""Model-level tests for the smart job-search entities.

These verify the new tables persist, their relationships resolve, and that
deleting a user cascades to all of their job-search data.
"""

from __future__ import annotations

from app.core.security import hash_password
from app.models import (
    AutomationRule,
    Certificate,
    Cv,
    CvSource,
    Job,
    JobSearchFilter,
    RunFrequency,
    Skill,
    SkillProficiency,
    SourcedApplication,
    SourcedApplicationStatus,
    User,
)
from sqlalchemy import select
from sqlalchemy.orm import Session


def _make_user(db: Session) -> User:
    user = User(email="vault@example.com", hashed_password=hash_password("Sup3rSecret!"))
    db.add(user)
    db.flush()
    return user


def test_document_vault_relationships(db_session: Session) -> None:
    user = _make_user(db_session)
    db_session.add_all(
        [
            Cv(user_id=user.id, title="Base CV", source=CvSource.UPLOADED),
            Certificate(user_id=user.id, name="AWS SAA", issuer="Amazon"),
            Skill(user_id=user.id, name="Python", proficiency=SkillProficiency.EXPERT),
        ]
    )
    db_session.commit()
    db_session.refresh(user)

    assert len(user.cvs) == 1
    assert len(user.certificates) == 1
    assert len(user.skills) == 1
    assert user.cvs[0].source == CvSource.UPLOADED


def test_job_filter_automation_and_sourced_application(db_session: Session) -> None:
    user = _make_user(db_session)

    job = Job(
        user_id=user.id,
        source="adzuna",
        external_id="abc-123",
        title="Senior Engineer",
        url="https://example.com/jobs/abc-123",
    )
    filt = JobSearchFilter(user_id=user.id, name="Remote backend", remote=True)
    db_session.add_all([job, filt])
    db_session.flush()

    cv = Cv(user_id=user.id, title="Tailored", source=CvSource.AI_TAILORED, job_id=job.id)
    db_session.add(cv)
    db_session.flush()

    db_session.add_all(
        [
            AutomationRule(user_id=user.id, filter_id=filt.id, run_frequency=RunFrequency.WEEKLY),
            SourcedApplication(
                user_id=user.id,
                job_id=job.id,
                cv_id=cv.id,
                status=SourcedApplicationStatus.SAVED,
                source_url=job.url,
            ),
        ]
    )
    db_session.commit()
    db_session.refresh(user)

    assert user.automation_rules[0].filter.name == "Remote backend"
    assert user.sourced_applications[0].job.title == "Senior Engineer"
    assert user.sourced_applications[0].cv_id == cv.id


def test_deleting_user_cascades_to_job_search_data(db_session: Session) -> None:
    user = _make_user(db_session)
    job = Job(user_id=user.id, source="adzuna", external_id="x", title="T", url="https://x")
    db_session.add_all([job, Skill(user_id=user.id, name="Go")])
    db_session.commit()

    db_session.delete(user)
    db_session.commit()

    assert db_session.scalars(select(Job)).first() is None
    assert db_session.scalars(select(Skill)).first() is None


def test_skill_name_unique_per_user(db_session: Session) -> None:
    user = _make_user(db_session)
    db_session.add(Skill(user_id=user.id, name="Rust"))
    db_session.commit()
    db_session.add(Skill(user_id=user.id, name="Rust"))
    try:
        db_session.commit()
        raised = False
    except Exception:
        db_session.rollback()
        raised = True
    assert raised, "duplicate (user_id, name) skill should violate the unique constraint"
