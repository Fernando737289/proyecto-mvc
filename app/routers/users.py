from fastapi import APIRouter, Depends
from app.models.user import (
    User, UpdateEstadoPersonaRequest
)
from app.models.schemas import PersonaOut
from app.services.user_service import (
    create_user, list_users, update_user, delete_user, update_estado_persona
)
from app.core.dependencies import require_admin
from app.services.auditoria_service import registrar_auditoria

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/", response_model=list[PersonaOut])
def list_all_users():
    return list_users()

@router.post("/usuarios")
async def registrar_usuario(
    payload: User,
    admin=Depends(require_admin)
):

    resultado = await create_user(payload)

    registrar_auditoria(
        tabla_afectada="persona",
        accion_realizada="INSERT",
        descripcion=f"Se registró la persona con RUT {payload.rut}",
        usuario_accion=admin["sub"]
    )

    return resultado

@router.put("/{id_persona}")
def update_users(
    id_persona: int,
    user: User,
    admin=Depends(require_admin)
):

    resultado = update_user(
        id_persona,
        user
    )

    registrar_auditoria(
        tabla_afectada="persona",
        accion_realizada="UPDATE",
        descripcion=f"Se actualizó la persona ID {id_persona}",
        usuario_accion=admin["sub"]
    )

    return resultado

@router.delete("/{id_persona}")
def delete_users(
    id_persona: int,
    admin=Depends(require_admin)
):

    resultado = delete_user(id_persona)

    registrar_auditoria(
        tabla_afectada="persona",
        accion_realizada="DELETE",
        descripcion=f"Se eliminó la persona ID {id_persona}",
        usuario_accion=admin["sub"]
    )

    return resultado

@router.patch("/{id_persona}/estado")
def cambiar_estado_persona(
    id_persona: int,
    data: UpdateEstadoPersonaRequest,
    admin=Depends(require_admin)
):

    resultado = update_estado_persona(
        id_persona,
        data.estado
    )

    registrar_auditoria(
        tabla_afectada="persona",
        accion_realizada="UPDATE",
        descripcion=f"Se cambió el estado de la persona ID {id_persona} a '{data.estado}'",
        usuario_accion=admin["sub"]
    )

    return resultado