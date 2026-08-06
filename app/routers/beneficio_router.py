from fastapi import APIRouter, Depends

from app.models.beneficio_model import Beneficio
from app.models.schemas import BeneficioOut
from app.services.beneficio_service import (
    create_beneficio,
    list_beneficios,
    update_beneficio,
    delete_beneficio
)
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/beneficios",
    tags=["Beneficios"]
)

@router.post("/crear")
def crear_beneficio(
    data: Beneficio,
    admin = Depends(require_admin)
):

    return create_beneficio(data)

@router.get("/", response_model=list[BeneficioOut])
def obtener_beneficios():

    return list_beneficios()

@router.put("/actualizar/{id_beneficio}")
def actualizar_beneficio(
    id_beneficio: int, 
    data: Beneficio,
    admin = Depends(require_admin)
):

    return update_beneficio(id_beneficio, data)


@router.delete("/eliminar/{id_beneficio}")
def eliminar_beneficio(
    id_beneficio: int,
    admin = Depends(require_admin)
):

    return delete_beneficio(id_beneficio)