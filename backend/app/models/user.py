from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """Tabela de usuários (ver diagrama do banco)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="user", server_default="user")
    daily_goal_xp: Mapped[int] = mapped_column(default=20, server_default="20")
    xp_total: Mapped[int] = mapped_column(default=0, server_default="0")
    level: Mapped[int] = mapped_column(default=1, server_default="1")
    current_streak: Mapped[int] = mapped_column(default=0, server_default="0")
    longest_streak: Mapped[int] = mapped_column(default=0, server_default="0")
    profile_public: Mapped[bool] = mapped_column(default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )