from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import (
    PersonaOut, UpdateEstadoPersonaRequest, UserCreate
)
from app.services.user_service import (
    create_user, list_users, update_user, delete_user, update_estado_persona
)
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=list[PersonaOut])
def list_all_users(db: Session = Depends(get_db)):
    return list_users(db)

@router.post("/usuarios")
async def registrar_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return await create_user(db, payload, admin["sub"])

@router.put("/{id_persona}")
def update_users(
    id_persona: int,
    user: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return update_user(db, id_persona, user, admin["sub"])

@router.delete("/{id_persona}")
def delete_users(
    id_persona: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return delete_user(db, id_persona, admin["sub"])

@router.patch("/{id_persona}/estado")
def cambiar_estado_persona(
    id_persona: int,
    data: UpdateEstadoPersonaRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return update_estado_persona(db, id_persona, data.estado, admin["sub"])
