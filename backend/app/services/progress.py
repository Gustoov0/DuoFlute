"""Regras de progresso, XP, nível, ofensiva e desbloqueio de lições."""
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import today_local
from app.models import (
    Exercise,
    ExerciseAttempt,
    Lesson,
    Section,
    Unit,
    User,
    UserActivityDay,
    UserLessonProgress,
    XpEvent,
)
from app.schemas.progress import LessonResult, ProgressSummary
from app.services import ranking

LEVEL_XP = 100          # XP necessário por nível
PERFECT_BONUS_XP = 5    # bônus por acertar tudo na primeira conclusão


def level_for(xp_total: int) -> int:
    return xp_total // LEVEL_XP + 1


# ---------------------------------------------------------------------------
# Trilha: ordem e desbloqueio
# ---------------------------------------------------------------------------
def ordered_lessons(db: Session) -> list[Lesson]:
    """Todas as lições na ordem da trilha: seção > unidade > posição."""
    stmt = (
        select(Lesson)
        .join(Unit, Lesson.unit_id == Unit.id)
        .join(Section, Unit.section_id == Section.id)
        .order_by(Section.position, Unit.position, Lesson.position)
    )
    return list(db.scalars(stmt))


def lesson_statuses(db: Session, user_id: int) -> list[tuple[Lesson, str, UserLessonProgress | None]]:
    """Estado de cada lição para o usuário.

    Regra de desbloqueio: uma lição só fica disponível quando todas as lições
    ESSENCIAIS anteriores foram concluídas.
    """
    progress = {
        p.lesson_id: p
        for p in db.scalars(select(UserLessonProgress).where(UserLessonProgress.user_id == user_id))
    }
    blocked = False
    rows: list[tuple[Lesson, str, UserLessonProgress | None]] = []
    for lesson in ordered_lessons(db):
        done = progress.get(lesson.id)
        if done is not None:
            lesson_status = "concluida"
        else:
            lesson_status = "bloqueada" if blocked else "disponivel"
            if lesson.is_essential:
                blocked = True
        rows.append((lesson, lesson_status, done))
    return rows


# ---------------------------------------------------------------------------
# Resumo do aluno
# ---------------------------------------------------------------------------
def effective_streak(db: Session, user: User) -> int:
    """Ofensiva atual. Se o aluno ficou mais de um dia sem praticar, ela zerou."""
    if user.current_streak == 0:
        return 0
    last = db.scalar(
        select(func.max(UserActivityDay.activity_date)).where(UserActivityDay.user_id == user.id)
    )
    if last is None or last < today_local() - timedelta(days=1):
        return 0
    return user.current_streak


def build_summary(db: Session, user: User) -> ProgressSummary:
    day = db.get(UserActivityDay, (user.id, today_local()))
    return ProgressSummary(
        xp_total=user.xp_total,
        level=user.level,
        xp_into_level=user.xp_total % LEVEL_XP,
        xp_per_level=LEVEL_XP,
        current_streak=effective_streak(db, user),
        longest_streak=user.longest_streak,
        daily_goal_xp=user.daily_goal_xp,
        xp_today=day.xp_earned if day else 0,
        goal_met_today=day.goal_met if day else False,
        active_today=day is not None,
    )


def set_daily_goal(db: Session, user: User, goal: int) -> ProgressSummary:
    user.daily_goal_xp = goal
    day = db.get(UserActivityDay, (user.id, today_local()))
    if day is not None:
        day.goal_met = day.xp_earned >= goal
    db.commit()
    db.refresh(user)
    return build_summary(db, user)


# ---------------------------------------------------------------------------
# Conclusão de lição
# ---------------------------------------------------------------------------
def complete_lesson(db: Session, user_id: int, lesson_id: int) -> LessonResult:
    # Trava a linha do usuário até o fim da transação. Se duas requisições
    # (inclusive em réplicas diferentes) tentarem concluir ao mesmo tempo, uma
    # espera a outra: evita XP duplicado. populate_existing garante dados novos.
    user = db.execute(
        select(User)
        .where(User.id == user_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).scalar_one()

    rows = lesson_statuses(db, user.id)
    position = next((i for i, row in enumerate(rows) if row[0].id == lesson_id), None)
    if position is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lição não encontrada.")
    lesson, lesson_status, existing = rows[position]
    if lesson_status == "bloqueada":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Conclua as lições anteriores primeiro.")

    # --- Acertos: usa a última resposta de cada pergunta corrigível ---
    exercises = db.scalars(select(Exercise).where(Exercise.lesson_id == lesson.id)).all()
    graded = [e for e in exercises if e.solution and "correct" in e.solution]
    latest: dict[int, ExerciseAttempt] = {}
    if graded:
        attempts = db.scalars(
            select(ExerciseAttempt)
            .where(
                ExerciseAttempt.user_id == user.id,
                ExerciseAttempt.exercise_id.in_([e.id for e in graded]),
            )
            .order_by(ExerciseAttempt.id)
        )
        for attempt in attempts:
            latest[attempt.exercise_id] = attempt  # a mais recente prevalece
    if any(e.id not in latest for e in graded):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Responda todas as perguntas antes de concluir a lição.")

    total = len(graded)
    correct = sum(1 for e in graded if latest[e.id].is_correct)
    score = round(100 * correct / total) if total else 100
    perfect = total > 0 and correct == total

    # --- Progresso da lição ---
    first_completion = existing is None
    if first_completion:
        db.add(UserLessonProgress(user_id=user.id, lesson_id=lesson.id, best_score=score))
    else:
        existing.attempts += 1
        existing.best_score = max(existing.best_score, score)

    # XP só na primeira conclusão. Repetir a lição serve de treino.
    xp_earned = 0
    if first_completion:
        xp_earned = lesson.xp_reward + (PERFECT_BONUS_XP if perfect else 0)

    # --- Ofensiva e meta diária ---
    today = today_local()
    day = db.get(UserActivityDay, (user.id, today))
    streak_increased = False
    if day is None:
        previous = db.scalar(
            select(func.max(UserActivityDay.activity_date)).where(
                UserActivityDay.user_id == user.id, UserActivityDay.activity_date < today
            )
        )
        if previous == today - timedelta(days=1):
            user.current_streak += 1
        else:
            user.current_streak = 1
        user.longest_streak = max(user.longest_streak, user.current_streak)
        streak_increased = True
        day = UserActivityDay(user_id=user.id, activity_date=today, xp_earned=0, goal_met=False)
        db.add(day)

    day.xp_earned += xp_earned
    was_met = day.goal_met
    day.goal_met = day.xp_earned >= user.daily_goal_xp

    # --- XP e nível ---
    old_level = user.level
    if xp_earned > 0:
        db.add(XpEvent(user_id=user.id, amount=xp_earned, source_type="lesson", source_id=lesson.id))
        user.xp_total += xp_earned
        user.level = level_for(user.xp_total)

    db.commit()

    # O banco já está correto; agora atualiza a cópia do ranking no Redis (melhor esforço)
    if xp_earned > 0:
        ranking.record_xp(db, user.id)

    # --- Próxima lição liberada? ---
    after = lesson_statuses(db, user.id)
    next_lesson_id = None
    if position + 1 < len(after) and after[position + 1][1] == "disponivel":
        next_lesson_id = after[position + 1][0].id

    return LessonResult(
        xp_earned=xp_earned,
        first_completion=first_completion,
        perfect=perfect,
        score=score,
        correct=correct,
        total=total,
        xp_total=user.xp_total,
        level=user.level,
        leveled_up=user.level > old_level,
        current_streak=user.current_streak,
        streak_increased=streak_increased,
        xp_today=day.xp_earned,
        daily_goal_xp=user.daily_goal_xp,
        goal_reached_now=day.goal_met and not was_met,
        next_lesson_id=next_lesson_id,
    )