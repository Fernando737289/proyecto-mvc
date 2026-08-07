import logging

from fastapi import HTTPException

from app.repository.historial_repository import (
    existe_persona,
    obtener_historial_persona
)

logger = logging.getLogger(__name__)


def get_historial_persona(db, id_persona: int):

    try:

        if not existe_persona(db, id_persona):

            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        historial = obtener_historial_persona(db, id_persona)

        return [
            {
                "beneficio": item.beneficio.nombre,
                "fecha_uso": item.fecha_uso,
                "codigo_canje": item.codigo_canje,
                "descuento": item.beneficio.valor_descuento,
                "comercio": item.beneficio.comercio
            }
            for item in historial
        ]

    except HTTPException:
        raise

    except Exception:

        logger.exception(
            "Error al obtener el historial de la persona %s",
            id_persona
        )

        raise HTTPException(
            status_code=500,
            detail="Error al obtener el historial de beneficios"
        )
