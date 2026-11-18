import socket

from fastapi import APIRouter, Depends, FastAPI, HTTPException
from redis.exceptions import RedisError
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.models import User
from app.routers import auth, learning, progress, ranking, users

# Todas as rotas ficam sob /api, igual ao que o Nginx vai encaminhar depois.
# A documentação automática (Swagger) também fica sob /api.
app = FastAPI(
    title="DuoFlute API",
    description="API do sistema de aprendizagem de flauta doce.",
    version="0.7.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

system_router = APIRouter(prefix="/api", tags=["Sistema"])


@system_router.get("/health")
def health():
    """Verifica se a API está de pé.

    Retorna também o nome do container que respondeu. Quando você escalar o
    back-end para várias réplicas, esse campo muda de uma requisição para
    outra, o que mostra o balanceamento de carga funcionando.
    """
    return {
        "status": "ok",
        "service": "duoflute-backend",
        "container": socket.gethostname(),
    }


@system_router.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    """Verifica se a API consegue falar com o banco e se a tabela users existe."""
    db.execute(text("SELECT 1"))
    total_users = db.scalar(select(func.count()).select_from(User))
    return {"status": "ok", "database": "conectado", "total_users": total_users}


@system_router.get("/health/cache")
def health_cache():
    """Verifica a conexão com o Redis."""
    r = get_redis()
    if r is None:
        raise HTTPException(503, "Redis não configurado.")
    try:
        r.ping()
        keys = r.dbsize()
        memory = r.info("memory")["used_memory_human"]
    except RedisError as exc:
        raise HTTPException(503, "Redis indisponível.") from exc
    return {"status": "ok", "cache": "conectado", "keys": keys, "used_memory": memory}


app.include_router(system_router)
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(learning.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(ranking.router, prefix="/api")