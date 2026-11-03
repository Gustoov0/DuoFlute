from typing import Any

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Valores usados em Lesson.lesson_type
LESSON_TYPES = (
    "apresentacao", "reconhecimento", "pratica", "combinacao", "revisao", "desafio",
)

# Valores usados em Exercise.exercise_type
EXERCISE_TYPES = (
    "informativo",          # cartão de conteúdo, sem resposta
    "multipla_escolha",
    "identificar_digitacao",
    "ouvir_e_reconhecer",
    "executar",             # o aluno toca (autoavaliação ou análise de áudio)
)


class Section(Base):
    """Grande etapa do aprendizado (ex.: 'Primeiras notas e digitação')."""

    __tablename__ = "sections"
    __table_args__ = (UniqueConstraint("position", name="uq_sections_position"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int]

    units: Mapped[list["Unit"]] = relationship(
        back_populates="section", order_by="Unit.position", cascade="all, delete-orphan"
    )


class Unit(Base):
    """Conteúdo específico dentro de uma seção (ex.: 'Nota Si')."""

    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("section_id", "position", name="uq_units_section_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("sections.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(150))
    objective: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int]

    section: Mapped["Section"] = relationship(back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="unit", order_by="Lesson.position", cascade="all, delete-orphan"
    )


class Lesson(Base):
    """Atividade interativa dentro de uma unidade."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("unit_id", "position", name="uq_lessons_unit_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(150))
    lesson_type: Mapped[str] = mapped_column(String(30))
    position: Mapped[int]
    xp_reward: Mapped[int] = mapped_column(default=10, server_default="10")
    is_essential: Mapped[bool] = mapped_column(default=True, server_default="true")

    unit: Mapped["Unit"] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson", order_by="Exercise.position", cascade="all, delete-orphan"
    )


class Exercise(Base):
    """Uma pergunta ou atividade dentro de uma lição."""

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("lesson_id", "position", name="uq_exercises_lesson_position"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    exercise_type: Mapped[str] = mapped_column(String(40))
    position: Mapped[int]
    difficulty: Mapped[int] = mapped_column(default=1, server_default="1")

    # O que o aluno vê: enunciado, opções, diagramas...
    content: Mapped[dict[str, Any]] = mapped_column(JSONB)
    # Gabarito. NUNCA é enviado ao cliente: a correção acontece no servidor.
    solution: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    lesson: Mapped["Lesson"] = relationship(back_populates="exercises")