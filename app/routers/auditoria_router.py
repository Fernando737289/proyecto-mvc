from fastapi import APIRouter, Depends

from app.models.schemas import AuditoriaOut
from app.services.auditoria_service import list_auditoria
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"]
)


@router.get("/", response_model=list[AuditoriaOut])
def obtener_auditoria(
    admin=Depends(require_admin)
):
    
    return list_auditoria()
