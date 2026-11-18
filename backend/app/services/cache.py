"""Cache-aside em Redis para conteúdo que muda pouco (trilha, notas)."""
import logging
from collections.abc import Callable

from redis.exceptions import RedisError

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


def cached_json(key: str, ttl: int, build: Callable[[], bytes]) -> tuple[bytes, str]:
    """Devolve (JSON em bytes, estado). Estado: HIT, MISS ou BYPASS (Redis fora do ar).

    HIT: veio do Redis. MISS: foi calculado agora e guardado.
    Se o Redis falhar, a resposta é calculada normalmente: o cache é só uma otimização.
    """
    r = get_redis()
    if r is None:
        return build(), "BYPASS"
    try:
        hit = r.get(key)
        if hit is not None:
            return hit.encode("utf-8"), "HIT"
    except RedisError as exc:
        logger.warning("Redis indisponível na leitura do cache: %s", exc)
        return build(), "BYPASS"

    payload = build()
    try:
        r.set(key, payload.decode("utf-8"), ex=ttl)
    except RedisError as exc:
        logger.warning("Redis indisponível ao gravar o cache: %s", exc)
        return payload, "BYPASS"
    return payload, "MISS"


def invalidate(pattern: str) -> int:
    """Apaga as chaves que casam com o padrão (ex.: 'cache:learning:*')."""
    r = get_redis()
    if r is None:
        return 0
    try:
        keys = list(r.scan_iter(match=pattern))
        return r.delete(*keys) if keys else 0
    except RedisError as exc:
        logger.warning("Não foi possível invalidar o cache: %s", exc)
        return 0