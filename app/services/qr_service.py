import logging
import qrcode
from io import BytesIO
import base64

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repository.qr_repository import (
    get_persona_by_rut as repo_get_persona_by_rut
)
from app.repository.tarjeta_repository import (
    get_tarjeta as repo_get_tarjeta,
    actualizar_codigo_qr
)
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


def get_persona_by_rut(db: Session, rut: str):

    persona = repo_get_persona_by_rut(db, rut)

    if not persona:

        raise HTTPException(
            status_code=404,
            detail="Persona no encontrada"
        )

    return persona


def generar_qr(persona):

    contenido = f"""
    Rut: {persona.rut}
    Nombre: {persona.nombres}
    Apellidos: {persona.apellidos}
    """

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )

    qr.add_data(contenido)

    qr.make(fit=True)

    imagen_qr = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()

    imagen_qr.save(buffer, format="PNG")

    buffer.seek(0)

    base64_qr = base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")

    return base64_qr


def regenerar_qr(db: Session, rut: str, usuario_accion: str):

    try:

        persona = get_persona_by_rut(db, rut)

        tarjeta = repo_get_tarjeta(db, rut=rut)

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="La persona no posee una tarjeta"
            )

        codigo_qr = generar_qr(persona)

        actualizar_codigo_qr(db, tarjeta.id_tarjeta, codigo_qr)

        registrar_auditoria(
            db,
            tabla_afectada="tarjeta",
            accion_realizada="UPDATE",
            descripcion=f"Se regeneró el QR de la tarjeta ID {tarjeta.id_tarjeta}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "codigo_qr": codigo_qr
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al regenerar el QR del RUT %s",
            rut
        )

        raise HTTPException(
            status_code=500,
            detail="Error al generar el QR"
        )
