from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ProgressSummary(BaseModel):
    xp_total: int
    level: int
    xp_into_level: int      # XP acumulado dentro do nível atual
    xp_per_level: int       # XP necessário para subir de nível
    current_streak: int     # já considera se a ofensiva foi quebrada
    longest_streak: int
    daily_goal_xp: int
    xp_today: int
    goal_met_today: bool
    active_today: bool


class LessonProgressOut(BaseModel):
    lesson_id: int
    status: Literal["concluida", "disponivel", "bloqueada"]
    best_score: int | None
    attempts: int | None
    completed_at: datetime | None


class LessonResult(BaseModel):
    xp_earned: int
    first_completion: bool
    perfect: bool
    score: int              # 0 a 100
    correct: int
    total: int
    xp_total: int
    level: int
    leveled_up: bool
    current_streak: int
    streak_increased: bool
    xp_today: int
    daily_goal_xp: int
    goal_reached_now: bool
    next_lesson_id: int | None


class GoalIn(BaseModel):
    daily_goal_xp: Literal[10, 20, 30, 50]