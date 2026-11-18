from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.ranking import WeeklyRanking
from app.services import ranking as service

router = APIRouter(prefix="/ranking", tags=["Ranking"])


@router.get("/weekly", response_model=WeeklyRanking)
def weekly_ranking(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ranking de XP da semana (segunda a domingo) e a posição do aluno logado."""
    return service.get_weekly(db, current_user.id, limit)