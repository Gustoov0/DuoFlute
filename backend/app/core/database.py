from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# O "engine" gerencia as conexões com o PostgreSQL.
# pool_pre_ping testa a conexão antes de usá-la (evita erro se o banco reiniciou).
engine = create_engine(settings.database_url, pool_pre_ping=True)

# Cada requisição abre uma "sessão" (uma conversa com o banco) e a fecha no final.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe base de todos os modelos (tabelas)."""


def get_db():
    """Dependência do FastAPI: entrega uma sessão e garante que ela seja fechada."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()