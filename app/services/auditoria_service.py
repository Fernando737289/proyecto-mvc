import logging

from fastapi import HTTPException

from app.repository.auditoria_repository import (
    insertar_auditoria,
    obtener_auditoria as repo_obtener_auditoria
)

logger = logging.getLogger(__name__)


def registrar_auditoria(
    db,
    tabla_afectada: str,
    accion_realizada: str,
    descripcion: str,
    usuario_accion: str
):

    try:

        insertar_auditoria(
            db,
            tabla_afectada,
            accion_realizada,
            descripcion,
            usuario_accion
        )

    except Exception:

        db.rollback()

        logger.exception(
            "Error al registrar auditoría (%s %s por %s)",
            tabla_afectada,
            accion_realizada,
            usuario_accion
        )

        raise HTTPException(
            status_code=500,
            detail="Error al registrar la auditoría"
        )


def list_auditoria(db):

    try:

        return repo_obtener_auditoria(db)

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al obtener auditoría"
        )
