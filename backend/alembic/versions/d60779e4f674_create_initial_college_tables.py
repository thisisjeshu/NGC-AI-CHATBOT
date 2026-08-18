"""Create initial college tables

Revision ID: d60779e4f674
Revises:
Create Date: 2026-08-10 13:12:30.093585
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d60779e4f674"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the original college tables."""

    # Departments
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("short_name", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("short_name"),
    )

    op.create_index(
        "ix_departments_id",
        "departments",
        ["id"],
        unique=False,
    )

    # Programmes
    op.create_table(
        "programmes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("short_name", sa.String(length=50), nullable=True),
        sa.Column("level", sa.String(length=50), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_programmes_id",
        "programmes",
        ["id"],
        unique=False,
    )

    # Faculty
    op.create_table(
        "faculty",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("designation", sa.String(length=100), nullable=True),
        sa.Column("email", sa.String(length=150), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_faculty_id",
        "faculty",
        ["id"],
        unique=False,
    )

    # Original notices table
    op.create_table(
        "notices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_notices_id",
        "notices",
        ["id"],
        unique=False,
    )

    # Original events table
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=250), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("venue", sa.String(length=200), nullable=True),
        sa.Column("event_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_events_id",
        "events",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the original college tables."""

    op.drop_index("ix_events_id", table_name="events")
    op.drop_table("events")

    op.drop_index("ix_notices_id", table_name="notices")
    op.drop_table("notices")

    op.drop_index("ix_faculty_id", table_name="faculty")
    op.drop_table("faculty")

    op.drop_index("ix_programmes_id", table_name="programmes")
    op.drop_table("programmes")

    op.drop_index("ix_departments_id", table_name="departments")
    op.drop_table("departments")