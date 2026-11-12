from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Exercise, Lesson, Note, Section, Unit, User
from app.schemas.learning import AnswerIn, AnswerOut, LessonDetail, NoteOut, SectionOut

router = APIRouter(prefix="/learning", tags=["Aprendizagem"])


@router.get("/path", response_model=list[SectionOut])
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trilha completa: seções > unidades > lições (sem os exercícios)."""
    stmt = (
        select(Section)
        .options(selectinload(Section.units).selectinload(Unit.lessons))
        .order_by(Section.position)
    )
    return db.scalars(stmt).all()


@router.get("/lessons/{lesson_id}", response_model=LessonDetail)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Uma lição com seus exercícios (sem gabarito)."""
    lesson = db.scalar(
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(selectinload(Lesson.exercises))
    )
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lição não encontrada.")
    return lesson


@router.get("/notes", response_model=list[NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Notas com suas digitações (biblioteca de digitações)."""
    stmt = select(Note).options(selectinload(Note.fingering)).order_by(Note.id)
    return db.scalars(stmt).all()


@router.post("/exercises/{exercise_id}/answer", response_model=AnswerOut)
def answer_exercise(
    exercise_id: int,
    data: AnswerIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Corrige a resposta de um exercício. O gabarito só existe no servidor."""
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Exercício não encontrado.")

    solution = exercise.solution or {}
    if "correct" not in solution:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Este exercício não possui correção automática.",
        )

    correct_answer = str(solution["correct"])
    return AnswerOut(correct=data.answer == correct_answer, correct_answer=correct_answer)