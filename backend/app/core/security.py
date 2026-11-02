from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings

_hasher = PasswordHasher()  # Argon2id, com sal aleatório embutido no hash

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Gera o hash da senha. A senha original nunca é guardada."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Confere se a senha digitada corresponde ao hash guardado."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: int) -> str:
    """Cria um JWT assinado. 'sub' (subject) identifica o dono do token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Valida assinatura e validade do token. Retorna o id do usuário ou None."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None