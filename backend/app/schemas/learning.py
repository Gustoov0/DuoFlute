from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FingeringOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    holes: dict[str, int]


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name_pt: str
    scientific_name: str
    frequency_hz: float
    staff_position: int
    introduced_in_unit_id: int | None
    fingering: FingeringOut | None


class ExerciseOut(BaseModel):
    """Repare: NÃO tem o campo 'solution'. O gabarito nunca sai do servidor."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_type: str
    position: int
    difficulty: int
    content: dict[str, Any]


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    lesson_type: str
    position: int
    xp_reward: int
    is_essential: bool


class LessonDetail(LessonSummary):
    unit_id: int
    exercises: list[ExerciseOut]


class UnitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    objective: str | None
    position: int
    lessons: list[LessonSummary]


class SectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    position: int
    units: list[UnitOut]


class AnswerIn(BaseModel):
    answer: str = Field(min_length=1, max_length=50)


class AnswerOut(BaseModel):
    correct: bool
    correct_answer: str