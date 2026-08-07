from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import HistorialOut
from app.services.canjes_service import canjear_beneficio
from app.services.historial_beneficio_service import get_historial_persona

router = APIRouter(
    prefix="/beneficios",
    tags=["Beneficios"]
)


@router.post("/canjear")
def canjear(
    id_persona: int,
    id_beneficio: int,
    db: Session = Depends(get_db)
):
    return canjear_beneficio(
        db,
        id_persona,
        id_beneficio
    )

@router.get("/historial/{id_persona}", response_model=list[HistorialOut])
def historial_persona(id_persona: int, db: Session = Depends(get_db)):

    return get_historial_persona(db, id_persona)
