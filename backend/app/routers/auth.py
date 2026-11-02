from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas.user import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["Autenticação"])


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
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Valida e-mail e senha e devolve um token de acesso (JWT)."""
    user = db.scalar(select(User).where(User.email == data.email.lower()))

    # Mesma mensagem para "e-mail não existe" e "senha errada",
    # para não revelar quais e-mails estão cadastrados.
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos.",
        )

    return Token(
        access_token=create_access_token(user.id),
        expires_in=settings.jwt_expire_minutes * 60,
    )