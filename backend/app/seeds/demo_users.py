"""Cria alunos de demonstração com XP nesta semana (para testar o ranking).

Uso, dentro do container do back-end:
    python -m app.seeds.demo_users            # cria os alunos
    python -m app.seeds.demo_users --remove   # remove os alunos

Senha de todos: demo12345
"""
import argparse

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import User, XpEvent
from app.services import ranking
from app.services.progress import level_for

DEMO_USERS = [("Ana", 85), ("Bruno", 60), ("Carla", 45), ("Diego", 30), ("Elisa", 15)]


def email_for(index: int) -> str:
    return f"aluno{index}@duoflute.dev"


def create() -> None:
    with SessionLocal() as db:
        for index, (name, xp) in enumerate(DEMO_USERS, start=1):
            if db.scalar(select(User).where(User.email == email_for(index))):
                print(f"  {name}: já existe")
                continue
            user = User(
                email=email_for(index),
                password_hash=hash_password("demo12345"),
                display_name=name,
                xp_total=xp,
                level=level_for(xp),
            )
            db.add(user)
            db.flush()
            db.add(XpEvent(user_id=user.id, amount=xp, source_type="demo", source_id=None))
            db.commit()
            ranking.record_xp(db, user.id)
            print(f"  {name}: criado com {xp} XP")
    print("Pronto.")


def remove() -> None:
    with SessionLocal() as db:
        emails = [email_for(i) for i in range(1, len(DEMO_USERS) + 1)]
        db.execute(delete(User).where(User.email.in_(emails)))  # o banco apaga o XP em cascata
        db.commit()
    # O ranking só cresce (ZADD GT), então precisa ser reconstruído após remover XP
    ranking.invalidate_current_week()
    print("Alunos de demonstração removidos.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Alunos de demonstração.")
    parser.add_argument("--remove", action="store_true", help="remove os alunos")
    remove() if parser.parse_args().remove else create()