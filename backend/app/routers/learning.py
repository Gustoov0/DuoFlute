from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Exercise, ExerciseAttempt, Lesson, Note, Section, Unit, User
from app.schemas.learning import AnswerIn, AnswerOut, LessonDetail, NoteOut, SectionOut
from app.services.cache import cached_json

router = APIRouter(prefix="/learning", tags=["Aprendizagem"])

# O conteúdo muda raramente (só quando o seed roda), então vai para o cache do Redis.
CONTENT_CACHE_TTL = 300  # segundos
_PATH_JSON = TypeAdapter(list[SectionOut])
_NOTES_JSON = TypeAdapter(list[NoteOut])


@router.get("/path", response_model=list[SectionOut])
def get_learning_path(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trilha completa: seções > unidades > lições (sem os exercícios).

    O cabeçalho X-Cache indica se a resposta veio do cache (HIT) ou do banco (MISS).
    """

    def build() -> bytes:
        stmt = (
            select(Section)
            .options(selectinload(Section.units).selectinload(Unit.lessons))
            .order_by(Section.position)
        )
        sections = [SectionOut.model_validate(s) for s in db.scalars(stmt).all()]
        return _PATH_JSON.dump_json(sections)

    body, state = cached_json("cache:learning:path", CONTENT_CACHE_TTL, build)
    return Response(content=body, media_type="application/json", headers={"X-Cache": state})


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
    """Notas com suas digitações (biblioteca de digitações). Também usa o cache."""

    def build() -> bytes:
        stmt = select(Note).options(selectinload(Note.fingering)).order_by(Note.id)
        notes = [NoteOut.model_validate(n) for n in db.scalars(stmt).all()]
        return _NOTES_JSON.dump_json(notes)

    body, state = cached_json("cache:learning:notes", CONTENT_CACHE_TTL, build)
    return Response(content=body, media_type="application/json", headers={"X-Cache": state})


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
    is_correct = data.answer == correct_answer

    # Registra a tentativa: alimenta o cálculo de acertos e as estatísticas
    db.add(ExerciseAttempt(user_id=current_user.id, exercise_id=exercise.id, is_correct=is_correct))
    db.commit()

    return AnswerOut(correct=is_correct, correct_answer=correct_answer)