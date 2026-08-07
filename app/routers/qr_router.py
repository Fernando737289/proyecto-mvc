from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.schemas import QRRequest, QRResponse
from app.services.qr_service import regenerar_qr

router = APIRouter(
    prefix="/qr",
    tags=["QR"]
)


@router.post("/generar", response_model=QRResponse)
def generar_codigo_qr(
    data: QRRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    return regenerar_qr(db, data.rut, admin["sub"])
