"""Ranking semanal de XP.

Fonte da verdade: tabela xp_events (PostgreSQL).
O Redis guarda uma cópia derivada (sorted set) para leitura rápida.

Decisões importantes:
- Escrita IDEMPOTENTE e MONOTÔNICA: depois de gravar o XP no banco, calculamos o
  total da semana do aluno e fazemos ZADD ... GT (só atualiza se o novo valor for
  MAIOR). Repetir a operação ou executá-la fora de ordem, em réplicas diferentes,
  nunca duplica nem diminui pontos. (Um ZINCRBY somaria duas vezes numa corrida
  com a reconstrução do cache.)
- Se o Redis perder os dados, o ranking é reconstruído a partir do PostgreSQL.
  Um lock no Redis impede que várias réplicas reconstruam ao mesmo tempo.
- Se o Redis estiver fora do ar, a leitura cai para o PostgreSQL (mais lenta, mas correta).
"""
import logging
from datetime import date, datetime, time, timedelta

from redis.exceptions import RedisError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import local_tz, today_local
from app.core.redis_client import get_redis
from app.models import User, XpEvent
from app.schemas.ranking import RankingEntry, RankingMe, WeeklyRanking

logger = logging.getLogger(__name__)

KEY_TTL_SECONDS = 21 * 24 * 3600   # a chave da semana some sozinha depois de 3 semanas
LOCK_TTL_SECONDS = 15
ANONYMOUS_NAME = "Aluno anônimo"


class _Unavailable(Exception):
    """O ranking no Redis não pôde ser usado nesta requisição."""


# ---------------------------------------------------------------------------
# Semana e chaves
# ---------------------------------------------------------------------------
def week_bounds(day: date) -> tuple[date, date]:
    """(segunda-feira, próxima segunda-feira). O fim é exclusivo."""
    start = day - timedelta(days=day.weekday())
    return start, start + timedelta(days=7)


def week_key(start: date) -> str:
    iso = start.isocalendar()
    return f"ranking:weekly:{iso.year}-W{iso.week:02d}"


def _ready_key(key: str) -> str:
    return f"{key}:ready"


def _bounds_datetimes(start: date, end: date) -> tuple[datetime, datetime]:
    tz = local_tz()
    return datetime.combine(start, time.min, tzinfo=tz), datetime.combine(end, time.min, tzinfo=tz)


# ---------------------------------------------------------------------------
# Consultas ao PostgreSQL (fonte da verdade)
# ---------------------------------------------------------------------------
def _totals_from_db(db: Session, start: date, end: date) -> list[tuple[int, int]]:
    """[(user_id, xp)] da semana, do maior para o menor."""
    lo, hi = _bounds_datetimes(start, end)
    total = func.sum(XpEvent.amount)
    stmt = (
        select(XpEvent.user_id, total)
        .where(XpEvent.created_at >= lo, XpEvent.created_at < hi)
        .group_by(XpEvent.user_id)
        .having(total > 0)
        .order_by(total.desc(), XpEvent.user_id)
    )
    return [(user_id, int(xp)) for user_id, xp in db.execute(stmt)]


def _user_total(db: Session, user_id: int, start: date, end: date) -> int:
    lo, hi = _bounds_datetimes(start, end)
    return int(
        db.scalar(
            select(func.coalesce(func.sum(XpEvent.amount), 0)).where(
                XpEvent.user_id == user_id,
                XpEvent.created_at >= lo,
                XpEvent.created_at < hi,
            )
        )
        or 0
    )


# ---------------------------------------------------------------------------
# Escrita no Redis
# ---------------------------------------------------------------------------
def record_xp(db: Session, user_id: int) -> None:
    """Atualiza o ranking depois que o XP foi gravado no banco (melhor esforço)."""
    r = get_redis()
    if r is None:
        return
    start, end = week_bounds(today_local())
    total = _user_total(db, user_id, start, end)
    if total <= 0:
        return
    key = week_key(start)
    try:
        r.zadd(key, {str(user_id): total}, gt=True)
        r.expire(key, KEY_TTL_SECONDS)
    except RedisError as exc:
        logger.warning("Redis indisponível ao atualizar o ranking: %s", exc)


def invalidate_current_week() -> None:
    """Descarta a cópia do ranking da semana; a próxima leitura reconstrói."""
    r = get_redis()
    if r is None:
        return
    key = week_key(week_bounds(today_local())[0])
    try:
        r.delete(key, _ready_key(key))
    except RedisError as exc:
        logger.warning("Redis indisponível ao invalidar o ranking: %s", exc)


def _rebuild(db: Session, r, key: str, start: date, end: date) -> bool:
    """Recria o ranking no Redis a partir do banco. False se outra réplica já está fazendo isso."""
    lock_key = f"{key}:lock"
    if not r.set(lock_key, "1", nx=True, ex=LOCK_TTL_SECONDS):
        return False
    try:
        rows = _totals_from_db(db, start, end)
        pipe = r.pipeline()
        if rows:
            pipe.zadd(key, {str(user_id): xp for user_id, xp in rows}, gt=True)
            pipe.expire(key, KEY_TTL_SECONDS)
        pipe.set(_ready_key(key), "1", ex=KEY_TTL_SECONDS)
        pipe.execute()
        return True
    finally:
        r.delete(lock_key)


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------
def _read_redis(db: Session, r, me_id: int, limit: int, start: date, end: date):
    key = week_key(start)
    if not r.exists(_ready_key(key)):
        # Primeira leitura da semana, ou o Redis perdeu os dados: reconstrói
        if not _rebuild(db, r, key, start, end):
            raise _Unavailable()
    top = [(int(member), int(score)) for member, score in r.zrevrange(key, 0, limit - 1, withscores=True)]
    position = r.zrevrank(key, str(me_id))
    score = r.zscore(key, str(me_id))
    me = RankingMe(rank=position + 1, xp=int(score)) if position is not None and score is not None else None
    return top, me


def _read_db(db: Session, me_id: int, limit: int, start: date, end: date):
    rows = _totals_from_db(db, start, end)
    me = None
    for index, (user_id, xp) in enumerate(rows):
        if user_id == me_id:
            me = RankingMe(rank=index + 1, xp=xp)
            break
    return rows[:limit], me


def get_weekly(db: Session, me_id: int, limit: int) -> WeeklyRanking:
    start, end = week_bounds(today_local())

    result = None
    source = "redis"
    r = get_redis()
    if r is not None:
        try:
            result = _read_redis(db, r, me_id, limit, start, end)
        except (RedisError, _Unavailable) as exc:
            logger.warning("Ranking via Redis indisponível, usando o banco: %r", exc)

    if result is None:
        source = "database"
        result = _read_db(db, me_id, limit, start, end)

    top, me = result
    ids = [user_id for user_id, _ in top]
    users = {u.id: u for u in db.scalars(select(User).where(User.id.in_(ids)))} if ids else {}

    entries = []
    for index, (user_id, xp) in enumerate(top):
        user = users.get(user_id)
        if user is None:
            continue
        # Respeita a privacidade: perfis não públicos aparecem sem nome
        name = user.display_name if (user.profile_public or user_id == me_id) else ANONYMOUS_NAME
        entries.append(
            RankingEntry(rank=index + 1, user_id=user_id, display_name=name, xp=xp, is_me=user_id == me_id)
        )

    return WeeklyRanking(
        week_start=start,
        week_end=end - timedelta(days=1),
        source=source,
        entries=entries,
        me=me,
    )