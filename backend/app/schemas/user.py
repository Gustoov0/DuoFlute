from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Dados recebidos no cadastro."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    """Dados recebidos no login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Dados devolvidos ao cliente. Repare: NÃO inclui password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    display_name: str
    avatar_url: str | None
    role: str
    daily_goal_xp: int
    xp_total: int
    level: int
    current_streak: int
    longest_streak: int
    profile_public: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # segundos