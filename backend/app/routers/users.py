from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models import User
from app.schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["Usuários"])


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """Retorna os dados do usuário logado. Exige token."""
    return current_user