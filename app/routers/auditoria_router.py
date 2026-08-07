from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import AuditoriaOut
from app.services.auditoria_service import list_auditoria
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/auditoria",
    tags=["Auditoria"]
)


@router.get("/", response_model=list[AuditoriaOut])
def obtener_auditoria(
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):

    return list_auditoria(db)
