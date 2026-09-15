"""interview question bank and contacts

Revision ID: 0004_prep_and_contacts
Revises: 0003_smart_job_search
Create Date: 2026-09-15 16:05:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import app.models.base
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0004_prep_and_contacts"
down_revision: str | None = "0003_smart_job_search"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "interview_questions",
        sa.Column("id", app.models.base.GUID(), nullable=False),
        sa.Column("user_id", app.models.base.GUID(), nullable=False),
        sa.Column("application_id", app.models.base.GUID(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("tags", sa.String(length=300), nullable=True),
        sa.Column("asked", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        # A prepared answer outlives the application it was written for, so the
        # question survives and is simply unlinked.
        sa.ForeignKeyConstraint(["application_id"], ["applications.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_interview_questions_application_id"),
        "interview_questions",
        ["application_id"],
    )
    op.create_index(op.f("ix_interview_questions_user_id"), "interview_questions", ["user_id"])

    op.create_table(
        "contacts",
        sa.Column("id", app.models.base.GUID(), nullable=False),
        sa.Column("user_id", app.models.base.GUID(), nullable=False),
        sa.Column("company_id", app.models.base.GUID(), nullable=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        # Deleting a company must not take its recruiters with it.
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_contacts_company_id"), "contacts", ["company_id"])
    op.create_index(op.f("ix_contacts_user_id"), "contacts", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_contacts_user_id"), table_name="contacts")
    op.drop_index(op.f("ix_contacts_company_id"), table_name="contacts")
    op.drop_table("contacts")
    op.drop_index(op.f("ix_interview_questions_user_id"), table_name="interview_questions")
    op.drop_index(op.f("ix_interview_questions_application_id"), table_name="interview_questions")
    op.drop_table("interview_questions")
