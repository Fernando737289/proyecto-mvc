import logging

from fastapi import HTTPException

from app.repository.usuario_repository import (
    buscar_usuario_por_username_email,
    crear_usuario as repo_crear_usuario
)
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


def create_usuario(db, data, usuario_accion="admin"):

    try:

        usuario = buscar_usuario_por_username_email(
            db,
            data.username,
            data.email
        )

        if usuario:

            raise HTTPException(
                status_code=400,
                detail="Usuario o correo ya registrado"
            )

        id_usuario = repo_crear_usuario(
            db,
            data.username,
            data.email,
            data.password
        )

        registrar_auditoria(
            db,
            tabla_afectada="usuario",
            accion_realizada="INSERT",
            descripcion=f"Se creó el usuario '{data.username}'",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "id_usuario": id_usuario,
            "mensaje": "Usuario creado correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al crear el usuario '%s'",
            data.username
        )

        raise HTTPException(
            status_code=500,
            detail="Error al crear el usuario"
        )
