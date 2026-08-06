from fastapi import APIRouter

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
    id_beneficio: int
):
    return canjear_beneficio(
        id_persona,
        id_beneficio
    )

@router.get("/historial/{id_persona}", response_model=list[HistorialOut])
def historial_persona(id_persona: int):

    return get_historial_persona(id_persona)
