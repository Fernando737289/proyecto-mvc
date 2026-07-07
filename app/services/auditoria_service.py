from fastapi import HTTPException

from app.repository.auditoria_repository import (
    registrar_auditoria,
    obtener_auditoria
)

def crear_auditoria(
    tabla_afectada: str,
    accion_realizada: str,
    descripcion: str,
    usuario_accion: str
):

    try:

        registrar_auditoria(
            tabla_afectada,
            accion_realizada,
            descripcion,
            usuario_accion
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al registrar auditoría: {str(e)}"
        )


def list_auditoria():

    try:

        return obtener_auditoria()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al obtener auditoría"
        )