"""Seed the database with realistic demo data.

Run as ``python -m app.seed``. Idempotent: if the demo user already exists the
script exits without duplicating data, so it is safe to run repeatedly (e.g. on
container start). The data is hand-written to resemble a real, in-progress job
search — varied companies, a believable spread of pipeline statuses, scheduled
interviews, follow-up tasks, and notes — so the UI and screenshots look
authentic rather than synthetic.
"""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.logging import configure_logging, get_logger
from app.core.security import hash_password
from app.models.application import Application
from app.models.base import utcnow
from app.models.company import Company
from app.models.enums import (
    ApplicationStatus,
    InterviewMode,
    InterviewResult,
    TaskPriority,
)
from app.models.interview import Interview
from app.models.note import Note
from app.models.task import Task
from app.models.user import User
from app.repositories.user import UserRepository

logger = get_logger("app.seed")

DEMO_EMAIL = "demo@careerflow.app"
# Intentional, publicly-documented demo credential — not a real secret.
DEMO_PASSWORD = "DemoPass123!"  # nosec B105

_COMPANIES = [
    ("Stripe", "Fintech", "https://stripe.com", "Remote (US)"),
    ("Datadog", "Observability", "https://datadoghq.com", "New York, NY"),
    ("Linear", "Developer Tools", "https://linear.app", "Remote"),
    ("Notion", "Productivity", "https://notion.so", "San Francisco, CA"),
    ("Vercel", "Cloud Platform", "https://vercel.com", "Remote"),
    ("Figma", "Design", "https://figma.com", "San Francisco, CA"),
    ("Cloudflare", "Security", "https://cloudflare.com", "Austin, TX"),
    ("Ramp", "Fintech", "https://ramp.com", "New York, NY"),
    ("Airbnb", "Travel", "https://airbnb.com", "Remote (US)"),
    ("Sentry", "Developer Tools", "https://sentry.io", "Remote"),
]


# A realistic, in-progress search: a wider funnel at the top (applied/wishlist),
# a few advancing, a couple of offers, and the rejections that come with volume.
# Columns: company_index, role, status, salary_min, salary_max, remote, source, days_ago.
_APPLICATIONS = [
    (
        0,
        "Senior Backend Engineer",
        ApplicationStatus.INTERVIEW,
        160000,
        200000,
        True,
        "Referral",
        21,
    ),
    (
        1,
        "Platform Engineer",
        ApplicationStatus.FINAL_INTERVIEW,
        150000,
        185000,
        False,
        "LinkedIn",
        28,
    ),
    (2, "Full-Stack Engineer", ApplicationStatus.OFFER, 140000, 175000, True, "Company site", 34),
    (3, "Backend Engineer", ApplicationStatus.ASSESSMENT, 135000, 170000, False, "LinkedIn", 9),
    (4, "Senior Software Engineer", ApplicationStatus.APPLIED, 155000, 195000, True, "Referral", 5),
    (5, "Product Engineer", ApplicationStatus.REJECTED, 145000, 180000, False, "Recruiter", 62),
    (6, "Systems Engineer", ApplicationStatus.ASSESSMENT, 140000, 180000, True, "Company site", 16),
    (
        7,
        "Software Engineer, Payments",
        ApplicationStatus.INTERVIEW,
        150000,
        185000,
        False,
        "Referral",
        44,
    ),
    (8, "Backend Engineer II", ApplicationStatus.APPLIED, 150000, 190000, True, "LinkedIn", 12),
    (9, "Full-Stack Engineer", ApplicationStatus.APPLIED, 140000, 175000, True, "Company site", 7),
    (0, "Staff Engineer", ApplicationStatus.WISHLIST, None, None, True, "Company site", 0),
    (
        7,
        "Senior Backend Engineer",
        ApplicationStatus.WISHLIST,
        None,
        None,
        False,
        "Company site",
        0,
    ),
    (2, "Engineering Manager", ApplicationStatus.ACCEPTED, 180000, 220000, True, "Referral", 95),
    (
        3,
        "Senior Frontend Engineer",
        ApplicationStatus.REJECTED,
        145000,
        180000,
        False,
        "LinkedIn",
        138,
    ),
    (5, "Design Engineer", ApplicationStatus.REJECTED, 140000, 175000, True, "Recruiter", 205),
    (
        1,
        "Site Reliability Engineer",
        ApplicationStatus.APPLIED,
        145000,
        180000,
        True,
        "LinkedIn",
        252,
    ),
]


def seed_demo_data(session: Session) -> bool:
    """Create the demo dataset if it does not already exist.

    Returns ``True`` when data was created, ``False`` when it already existed.
    """
    users = UserRepository(session)
    if users.get_by_email(DEMO_EMAIL) is not None:
        logger.info("demo data already present; skipping seed")
        return False

    now = utcnow()
    user = User(
        email=DEMO_EMAIL,
        hashed_password=hash_password(DEMO_PASSWORD),
        full_name="Demo Candidate",
    )
    session.add(user)
    session.flush()

    companies = [
        Company(user_id=user.id, name=name, industry=industry, website=website, location=location)
        for name, industry, website, location in _COMPANIES
    ]
    session.add_all(companies)
    session.flush()

    applications: list[Application] = []
    for company_idx, role, status, smin, smax, remote, source, days_ago in _APPLICATIONS:
        applied_at = (
            None if status == ApplicationStatus.WISHLIST else now - timedelta(days=days_ago)
        )
        application = Application(
            user_id=user.id,
            company_id=companies[company_idx].id,
            role_title=role,
            status=status,
            salary_min=smin,
            salary_max=smax,
            salary_currency="USD" if smin else None,
            location=companies[company_idx].location,
            is_remote=remote,
            application_url=f"{companies[company_idx].website}/careers",
            source=source,
            applied_at=applied_at,
        )
        applications.append(application)
    session.add_all(applications)
    session.flush()

    _seed_interviews(session, user, applications)
    _seed_tasks(session, user, applications)
    _seed_notes(session, user, applications)

    session.commit()
    logger.info("seeded demo data for %s", DEMO_EMAIL)
    return True


def _seed_interviews(session: Session, user: User, applications: list[Application]) -> None:
    now = utcnow()
    interviews = [
        Interview(
            user_id=user.id,
            application_id=applications[0].id,
            scheduled_at=now + timedelta(days=2),
            round_type="Technical screen",
            interviewer="Priya Sharma",
            mode=InterviewMode.VIDEO,
            result=InterviewResult.PENDING,
            notes="Focus on system design and API modelling.",
        ),
        Interview(
            user_id=user.id,
            application_id=applications[1].id,
            scheduled_at=now + timedelta(days=5),
            round_type="On-site loop",
            interviewer="Marcus Lee",
            mode=InterviewMode.ONSITE,
            result=InterviewResult.PENDING,
            notes="Four rounds: coding, design, behavioural, hiring manager.",
        ),
        Interview(
            user_id=user.id,
            application_id=applications[2].id,
            scheduled_at=now - timedelta(days=7),
            round_type="Final round",
            interviewer="Elena Rossi",
            mode=InterviewMode.VIDEO,
            result=InterviewResult.PASSED,
            notes="Went well — offer received the following week.",
        ),
        Interview(
            user_id=user.id,
            application_id=applications[7].id,
            scheduled_at=now + timedelta(days=3, hours=2),
            round_type="Hiring manager",
            interviewer="Daniel Okafor",
            mode=InterviewMode.VIDEO,
            result=InterviewResult.PENDING,
            notes="Discuss payments domain experience and team fit.",
        ),
        Interview(
            user_id=user.id,
            application_id=applications[12].id,
            scheduled_at=now - timedelta(days=30),
            round_type="Final panel",
            interviewer="Sofia Almeida",
            mode=InterviewMode.ONSITE,
            result=InterviewResult.PASSED,
            notes="Accepted the offer — start date confirmed.",
        ),
    ]
    session.add_all(interviews)


def _seed_tasks(session: Session, user: User, applications: list[Application]) -> None:
    base = utcnow()
    tasks = [
        Task(
            user_id=user.id,
            application_id=applications[0].id,
            title="Prepare system design notes for Stripe screen",
            priority=TaskPriority.HIGH,
            due_at=base + timedelta(days=1),
        ),
        Task(
            user_id=user.id,
            application_id=applications[1].id,
            title="Send availability for Datadog on-site",
            priority=TaskPriority.HIGH,
            due_at=base + timedelta(days=2),
        ),
        Task(
            user_id=user.id,
            application_id=applications[2].id,
            title="Review and respond to Linear offer",
            priority=TaskPriority.MEDIUM,
            due_at=base + timedelta(days=3),
        ),
        Task(
            user_id=user.id,
            title="Update resume with latest project",
            priority=TaskPriority.LOW,
            is_completed=True,
            completed_at=base - timedelta(days=2),
        ),
    ]
    session.add_all(tasks)


def _seed_notes(session: Session, user: User, applications: list[Application]) -> None:
    notes = [
        Note(
            user_id=user.id,
            application_id=applications[0].id,
            body=(
                "## Stripe — Senior Backend Engineer\n\n"
                "- Referred by a former colleague on the Payments team.\n"
                "- Stack: Ruby + Go, moving services to Go.\n"
                "- **Prep:** idempotency, rate limiting, ledger design."
            ),
        ),
        Note(
            user_id=user.id,
            application_id=applications[2].id,
            body=(
                "## Linear — offer details\n\n"
                "Base 165k + equity. Remote-first. Asked for a week to decide."
            ),
        ),
    ]
    session.add_all(notes)


def main() -> None:
    configure_logging(debug=True)
    session = SessionLocal()
    try:
        created = seed_demo_data(session)
        print("Seeded demo data." if created else "Demo data already present.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
