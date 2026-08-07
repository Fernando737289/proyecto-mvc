import logging

from fastapi import HTTPException

from app.repository.canje_repository import canjear_beneficio as canjear_beneficio_repo
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


def canjear_beneficio(
    db,
    id_persona: int,
    id_beneficio: int
):

    try:

        resultado = canjear_beneficio_repo(
            db,
            id_persona,
            id_beneficio
        )

        registrar_auditoria(
            db,
            tabla_afectada="historial_beneficios",
            accion_realizada="INSERT",
            descripcion=f"Se canjeó el beneficio ID {id_beneficio} para la persona ID {id_persona}",
            usuario_accion="publico"
        )

        db.commit()

        return resultado

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al canjear beneficio (persona=%s, beneficio=%s)",
            id_persona,
            id_beneficio
        )

        raise HTTPException(
            status_code=500,
            detail="Error al canjear el beneficio"
        )
