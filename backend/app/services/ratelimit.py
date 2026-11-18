"""Limite de tentativas com contador compartilhado no Redis.

Como o contador fica no Redis (e não na memória de cada réplica), o limite
vale para o sistema inteiro, não importa qual réplica receba a requisição.
"""
import logging

from redis.exceptions import RedisError

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def hit(key: str, limit: int, window_seconds: int) -> tuple[bool, int]:
    """Registra uma tentativa. Retorna (permitida, segundos até liberar).

    Janela fixa: o primeiro acesso inicia a contagem; ao expirar, zera.
    Se o Redis estiver fora do ar, libera (fail-open) para não derrubar o login.
    """
    r = get_redis()
    if r is None:
        return True, 0
    try:
        pipe = r.pipeline()  # as duas operações vão juntas, de forma atômica
        pipe.incr(key)
        pipe.expire(key, window_seconds, nx=True)  # só define o prazo se ainda não houver
        count, _ = pipe.execute()
        if count <= limit:
            return True, 0
        return False, max(r.ttl(key), 1)
    except RedisError as exc:
        logger.warning("Redis indisponível no limite de tentativas: %s", exc)
        return True, 0


def reset(key: str) -> None:
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(key)
    except RedisError as exc:
        logger.warning("Redis indisponível ao zerar o limite: %s", exc)