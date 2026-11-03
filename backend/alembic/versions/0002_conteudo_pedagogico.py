"""conteudo pedagogico: sections, units, lessons, exercises, notes, fingerings

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("position", name="uq_sections_position"),
    )

    op.create_table(
        "units",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("section_id", sa.Integer(), sa.ForeignKey("sections.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("objective", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("section_id", "position", name="uq_units_section_position"),
    )

    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("units.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("lesson_type", sa.String(30), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("is_essential", sa.Boolean(), nullable=False, server_default="true"),
        sa.UniqueConstraint("unit_id", "position", name="uq_lessons_unit_position"),
    )

    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("exercise_type", sa.String(40), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("solution", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.UniqueConstraint("lesson_id", "position", name="uq_exercises_lesson_position"),
    )

    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("introduced_in_unit_id", sa.Integer(), sa.ForeignKey("units.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name_pt", sa.String(50), nullable=False),
        sa.Column("scientific_name", sa.String(10), nullable=False),
        sa.Column("frequency_hz", sa.Float(), nullable=False),
        sa.Column("staff_position", sa.Integer(), nullable=False),
        sa.UniqueConstraint("name_pt", name="uq_notes_name_pt"),
    )

    op.create_table(
        "fingerings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("note_id", sa.Integer(), sa.ForeignKey("notes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("holes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.UniqueConstraint("note_id", name="uq_fingerings_note_id"),
    )


def downgrade() -> None:
    op.drop_table("fingerings")
    op.drop_table("notes")
    op.drop_table("exercises")
    op.drop_table("lessons")
    op.drop_table("units")
    op.drop_table("sections")