import redis

from app.core.config import settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis | None:
    """Cliente Redis compartilhado, ou None se o Redis não estiver configurado.

    Os timeouts são curtos de propósito: se o Redis cair, a API percebe rápido
    e segue funcionando sem ele, em vez de ficar travada esperando.
    """
    global _client
    if not settings.redis_url:
        return None
    if _client is None:
        _client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    return _client