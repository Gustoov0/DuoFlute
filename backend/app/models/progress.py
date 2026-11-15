from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserLessonProgress(Base):
    """Lição concluída por um usuário.

    Só existe linha para lições já concluídas. 'disponivel' e 'bloqueada'
    são calculadas na hora (ver app/services/progress.py).
    """

    __tablename__ = "user_lesson_progress"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="concluida", server_default="concluida")
    best_score: Mapped[int] = mapped_column(default=0, server_default="0")  # 0 a 100
    attempts: Mapped[int] = mapped_column(default=1, server_default="1")    # vezes concluída
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ExerciseAttempt(Base):
    """Cada resposta enviada a um exercício (certa ou errada)."""

    __tablename__ = "exercise_attempts"
    __table_args__ = (
        Index("ix_exercise_attempts_user_exercise", "user_id", "exercise_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"))
    is_correct: Mapped[bool]
    response_time_ms: Mapped[int | None]
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class XpEvent(Base):
    """Histórico de pontos de experiência (base do ranking semanal)."""

    __tablename__ = "xp_events"
    __table_args__ = (Index("ix_xp_events_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    amount: Mapped[int]
    source_type: Mapped[str] = mapped_column(String(30))   # lesson, song, mission, achievement
    source_id: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserActivityDay(Base):
    """Um dia em que o usuário praticou (base da ofensiva e da meta diária)."""

    __tablename__ = "user_activity_days"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    activity_date: Mapped[date] = mapped_column(Date, primary_key=True)
    xp_earned: Mapped[int] = mapped_column(default=0, server_default="0")
    goal_met: Mapped[bool] = mapped_column(default=False, server_default="false")