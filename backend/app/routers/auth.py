from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.user import Token, UserCreate, UserLogin, UserOut
from app.services import ratelimit

router = APIRouter(prefix="/auth", tags=["Autenticação"])

LOGIN_MAX_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60


def _client_ip(request: Request) -> str:
    # O gateway Nginx envia o IP real no cabeçalho X-Real-IP
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "desconhecido")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Cria uma nova conta."""
    email = data.email.lower()
    conflito = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Este e-mail já está cadastrado.",
    )

    if db.scalar(select(User).where(User.email == email)):
        raise conflito

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        display_name=data.display_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # dois cadastros simultâneos com o mesmo e-mail
        db.rollback()
        raise conflito
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Valida e-mail e senha e devolve um token de acesso (JWT).

    Limita as tentativas por IP + e-mail (contador no Redis, compartilhado entre
    as réplicas) para dificultar ataques de força bruta.
    """
    email = data.email.lower()
    limit_key = f"ratelimit:login:{_client_ip(request)}:{email}"

    allowed, retry_after = ratelimit.hit(limit_key, LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Muitas tentativas de login. Tente novamente em {retry_after} segundos.",
            headers={"Retry-After": str(retry_after)},
        )

    user = db.scalar(select(User).where(User.email == email))

    # Mesma mensagem para "e-mail não existe" e "senha errada",
    # para não revelar quais e-mails estão cadastrados.
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    ratelimit.reset(limit_key)  # login correto zera o contador
    return Token(
        access_token=create_access_token(user.id),
        expires_in=settings.jwt_expire_minutes * 60,
    )