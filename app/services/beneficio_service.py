import logging

from fastapi import HTTPException

from app.repository.beneficio_repository import (
    crear_beneficio as repo_crear_beneficio,
    obtener_beneficios as repo_obtener_beneficios,
    eliminar_beneficio as repo_eliminar_beneficio,
    actualizar_beneficio as repo_actualizar_beneficio
)
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


def create_beneficio(db, data, usuario_accion="admin"):

    try:

        id_beneficio = repo_crear_beneficio(db, data)

        registrar_auditoria(
            db,
            tabla_afectada="beneficio",
            accion_realizada="INSERT",
            descripcion=f"Se creó el beneficio '{data.nombre}'",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "id_beneficio": id_beneficio,
            "mensaje": "Beneficio creado correctamente"
        }

    except Exception:

        db.rollback()

        logger.exception(
            "Error al crear beneficio '%s'",
            data.nombre
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear el beneficio"
        )


def list_beneficios(db):

    try:

        return repo_obtener_beneficios(db)

    except Exception:

        logger.exception("Error al obtener beneficios")

        raise HTTPException(
            status_code=500,
            detail="Error al obtener beneficios"
        )


def delete_beneficio(db, id_beneficio: int, usuario_accion="admin"):

    try:

        filas = repo_eliminar_beneficio(db, id_beneficio)

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        registrar_auditoria(
            db,
            tabla_afectada="beneficio",
            accion_realizada="DELETE",
            descripcion=f"Se eliminó el beneficio ID {id_beneficio}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "mensaje": "Beneficio eliminado correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al eliminar el beneficio %s",
            id_beneficio
        )

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar beneficio"
        )


def update_beneficio(
    db,
    id_beneficio: int,
    data,
    usuario_accion="admin"
):

    try:

        filas = repo_actualizar_beneficio(
            db,
            id_beneficio,
            data
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        registrar_auditoria(
            db,
            tabla_afectada="beneficio",
            accion_realizada="UPDATE",
            descripcion=f"Se actualizó el beneficio ID {id_beneficio}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "mensaje": "Beneficio actualizado correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al actualizar el beneficio %s",
            id_beneficio
        )

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar beneficio"
        )
