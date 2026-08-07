from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import (
    CreateTarjetaRequest, TarjetaOut, UpdateTarjetaRequest
)
from app.services.tarjeta_service import (
    create_tarjeta,
    get_tarjeta,
    update_tarjeta,
    delete_tarjeta
)
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/tarjeta",
    tags=["Tarjeta"]
)

@router.post("/crear")
def crear_tarjeta(
    data: CreateTarjetaRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return create_tarjeta(
        db,
        data.rut,
        data.nombres,
        data.apellidos,
        data.telefono,
        admin["sub"]
    )

@router.get("/buscar", response_model=TarjetaOut)
def obtener_tarjeta(
    rut: str | None = None,
    numero_tarjeta: str | None = None,
    db: Session = Depends(get_db)
):

    return get_tarjeta(
        db,
        rut=rut,
        numero_tarjeta=numero_tarjeta
    )

@router.put("/{id_tarjeta}")
def actualizar_tarjeta(
    id_tarjeta: int,
    data: UpdateTarjetaRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return update_tarjeta(
        db,
        id_tarjeta,
        data.estado,
        data.fecha_vencimiento,
        admin["sub"]
    )

@router.delete("/{id_tarjeta}")
def eliminar_tarjeta(
    id_tarjeta: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return delete_tarjeta(db, id_tarjeta, admin["sub"])
