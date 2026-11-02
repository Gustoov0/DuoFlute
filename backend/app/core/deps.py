from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User

# Faz o botão "Authorize" aparecer no Swagger (/api/docs)
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependência que protege rotas: exige um token válido e devolve o usuário logado."""
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado ou sessão expirada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise erro
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise erro
    user = db.get(User, user_id)
    if user is None:
        raise erro
    return user