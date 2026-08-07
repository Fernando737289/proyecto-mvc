from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import BeneficioCreate, BeneficioOut
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
    data: BeneficioCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return create_beneficio(db, data, admin["sub"])

@router.get("/", response_model=list[BeneficioOut])
def obtener_beneficios(db: Session = Depends(get_db)):

    return list_beneficios(db)

@router.put("/actualizar/{id_beneficio}")
def actualizar_beneficio(
    id_beneficio: int,
    data: BeneficioCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return update_beneficio(db, id_beneficio, data, admin["sub"])


@router.delete("/eliminar/{id_beneficio}")
def eliminar_beneficio(
    id_beneficio: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return delete_beneficio(db, id_beneficio, admin["sub"])
