from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.progress import GoalIn, LessonProgressOut, LessonResult, ProgressSummary
from app.services import progress as service

router = APIRouter(prefix="/progress", tags=["Progresso"])


@router.get("/summary", response_model=ProgressSummary)
def get_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """XP, nível, ofensiva e meta diária do aluno."""
    return service.build_summary(db, current_user)


@router.get("/lessons", response_model=list[LessonProgressOut])
def get_lesson_statuses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Estado de cada lição (concluída, disponível ou bloqueada), na ordem da trilha."""
    return [
        LessonProgressOut(
            lesson_id=lesson.id,
            status=lesson_status,
            best_score=done.best_score if done else None,
            attempts=done.attempts if done else None,
            completed_at=done.completed_at if done else None,
        )
        for lesson, lesson_status, done in service.lesson_statuses(db, current_user.id)
    ]


@router.post("/lessons/{lesson_id}/complete", response_model=LessonResult)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Conclui uma lição: calcula acertos, concede XP e atualiza ofensiva e meta."""
    return service.complete_lesson(db, current_user.id, lesson_id)


@router.put("/goal", response_model=ProgressSummary)
def update_goal(
    data: GoalIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Altera a meta diária de XP."""
    return service.set_daily_goal(db, current_user, data.daily_goal_xp)