from fastapi import HTTPException

from app.repository.historial_repository import (
    obtener_historial_persona
)


def get_historial_persona(id_persona: int):

    try:

        historial = obtener_historial_persona(id_persona)

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

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al obtener el historial de beneficios"
        )