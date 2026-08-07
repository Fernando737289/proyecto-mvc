import logging
import random

from datetime import date, timedelta
from fastapi import HTTPException

from app.services.qr_service import (
    get_persona_by_rut,
    generar_qr
)
from app.repository.tarjeta_repository import (
    verificar_tarjeta_existente,
    crear_tarjeta as repo_crear_tarjeta,
    get_tarjeta as repo_get_tarjeta,
    get_tarjeta_by_id,
    update_tarjeta as repo_update_tarjeta,
    eliminar_tarjeta,
    obtener_tarjeta_por_id
)
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


def create_tarjeta(
    db,
    rut: str,
    nombres: str,
    apellidos: str,
    telefono: str | None = None,
    usuario_accion="admin"
):

    try:

        persona = get_persona_by_rut(db, rut)

        if persona.nombres.strip().lower() != nombres.strip().lower():
            raise HTTPException(
                status_code=400,
                detail="Los nombres no coinciden con los registros"
            )

        if persona.apellidos.strip().lower() != apellidos.strip().lower():
            raise HTTPException(
                status_code=400,
                detail="Los apellidos no coinciden con los registros"
            )

        if telefono:

            telefono_bd = persona.telefono

            if telefono_bd != telefono:
                raise HTTPException(
                    status_code=400,
                    detail="El teléfono no coincide con los registros"
                )

        tarjeta_existente = verificar_tarjeta_existente(
            db,
            persona.id_persona
        )

        if tarjeta_existente:
            raise HTTPException(
                status_code=400,
                detail="La persona ya posee una tarjeta"
            )

        codigo_qr = generar_qr(persona)

        numero_tarjeta = f"{random.randint(100000,999999)}"

        fecha_emision = date.today()

        fecha_vencimiento = fecha_emision + timedelta(days=365)

        id_tarjeta = repo_crear_tarjeta(
            db,
            persona.id_persona,
            numero_tarjeta,
            codigo_qr,
            fecha_emision,
            fecha_vencimiento,
            "activa"
        )

        registrar_auditoria(
            db,
            tabla_afectada="tarjeta",
            accion_realizada="INSERT",
            descripcion=f"Se creó una tarjeta para el RUT {rut}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "id_tarjeta": id_tarjeta,
            "numero_tarjeta": numero_tarjeta,
            "mensaje": "Tarjeta creada correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        logger.exception(
            "Error al crear tarjeta para RUT %s",
            rut
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear la tarjeta"
        )


def get_tarjeta(
    db,
    rut: str | None = None,
    numero_tarjeta: str | None = None
):

    try:

        if not rut and not numero_tarjeta:

            raise HTTPException(
                status_code=400,
                detail="Debe ingresar un rut o un número de tarjeta"
            )

        tarjeta = repo_get_tarjeta(
            db,
            rut,
            numero_tarjeta
        )

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        return {
            "id_persona": tarjeta.id_persona,
            "nombres": tarjeta.persona.nombres,
            "apellidos": tarjeta.persona.apellidos,
            "rut": tarjeta.persona.rut,
            "numero_tarjeta": tarjeta.numero_tarjeta,
            "codigo_qr": tarjeta.codigo_qr,
            "vigencia": tarjeta.fecha_vencimiento,
            "estado": tarjeta.estado
        }

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Error al obtener la tarjeta (rut=%s, numero_tarjeta=%s)",
            rut,
            numero_tarjeta
        )

        raise HTTPException(
            status_code=500,
            detail="Error al obtener la tarjeta"
        )


def update_tarjeta(
    db,
    id_tarjeta: int,
    estado: str,
    fecha_vencimiento,
    usuario_accion="admin"
):

    try:

        tarjeta = get_tarjeta_by_id(
            db,
            id_tarjeta
        )

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        repo_update_tarjeta(
            db,
            id_tarjeta,
            estado,
            fecha_vencimiento
        )

        registrar_auditoria(
            db,
            tabla_afectada="tarjeta",
            accion_realizada="UPDATE",
            descripcion=f"Se actualizó la tarjeta ID {id_tarjeta}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "id_tarjeta": id_tarjeta,
            "mensaje": "Tarjeta actualizada correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        logger.exception(
            "Error al actualizar la tarjeta %s",
            id_tarjeta
        )

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la tarjeta"
        )


def delete_tarjeta(db, id_tarjeta: int, usuario_accion="admin"):

    try:

        tarjeta = obtener_tarjeta_por_id(db, id_tarjeta)

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        eliminar_tarjeta(db, id_tarjeta)

        registrar_auditoria(
            db,
            tabla_afectada="tarjeta",
            accion_realizada="DELETE",
            descripcion=f"Se eliminó la tarjeta ID {id_tarjeta}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "id_tarjeta": id_tarjeta,
            "mensaje": "Tarjeta eliminada correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        logger.exception(
            "Error al eliminar la tarjeta %s",
            id_tarjeta
        )

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la tarjeta"
        )
