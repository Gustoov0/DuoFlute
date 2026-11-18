from datetime import date
from typing import Literal

from pydantic import BaseModel


class RankingEntry(BaseModel):
    rank: int
    user_id: int
    display_name: str
    xp: int
    is_me: bool


class RankingMe(BaseModel):
    rank: int
    xp: int


class WeeklyRanking(BaseModel):
    week_start: date            # segunda-feira
    week_end: date              # domingo (inclusive)
    source: Literal["redis", "database"]
    entries: list[RankingEntry]
    me: RankingMe | None        # None se o aluno ainda não pontuou na semana