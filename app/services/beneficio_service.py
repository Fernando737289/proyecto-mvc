from fastapi import HTTPException 

from app.repository.beneficio_repository import (
    crear_beneficio,
    obtener_beneficios,
    eliminar_beneficio,
    actualizar_beneficio
)

def create_beneficio(data):

    try:

        id_beneficio = crear_beneficio(data)

        return {
            "id_beneficio": id_beneficio,
            "mensaje": "Beneficio creado correctamente"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


def list_beneficios():

    try:

        return obtener_beneficios()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al obtener beneficios"
        )


def delete_beneficio(id_beneficio: int):

    try:

        filas = eliminar_beneficio(id_beneficio)

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        return {
            "mensaje": "Beneficio eliminado correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar beneficio"
        )


def update_beneficio(
    id_beneficio: int,
    data
):

    try:

        filas = actualizar_beneficio(
            id_beneficio,
            data
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        return {
            "mensaje": "Beneficio actualizado correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar beneficio"
        )