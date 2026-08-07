from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import CreateUsuarioRequest
from app.services.usuario_service import create_usuario
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/registro")
def registrar_usuario(
    data: CreateUsuarioRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return create_usuario(db, data, admin["sub"])
