import logging

from fastapi import HTTPException

from app.core.encryption import encrypt_data

from app.repository.user_repository import (
    existe_usuario_por_rut,
    insertar_usuario,
    obtener_personas,
    update_user_repository,
    delete_user_repository,
    update_estado_persona_repository
)

from app.services.dec_services import validar_vigencia_rut
from app.services.auditoria_service import registrar_auditoria

logger = logging.getLogger(__name__)


async def create_user(db, user, usuario_accion="admin"):

    resultado_dec = await validar_vigencia_rut(
        user_rut=user.rut,
        serial_number=user.serial_number
    )

    if not resultado_dec or resultado_dec.get("status") != 200:

        raise HTTPException(
            status_code=400,
            detail="No se pudo verificar la cédula con el servicio externo."
        )

    result_data = resultado_dec.get("result", {})

    if result_data.get("Verificacion") != "V":

        raise HTTPException(
            status_code=400,
            detail="La cédula de identidad no se encuentra vigente."
        )

    if existe_usuario_por_rut(db, user.rut):

        raise HTTPException(
            status_code=400,
            detail="Ya existe una persona registrada con ese RUT"
        )

    serial_encriptado = encrypt_data(
        user.serial_number
    )

    try:

        insertar_usuario(
            db,
            rut=user.rut,
            serial_number=serial_encriptado,
            nombres=user.nombres,
            apellidos=user.apellidos,
            direccion=user.direccion,
            numero_direccion=user.numero_direccion,
            telefono=user.telefono,
            email=user.email,
            fecha_nacimiento=user.fecha_nacimiento
        )

        registrar_auditoria(
            db,
            tabla_afectada="persona",
            accion_realizada="INSERT",
            descripcion=f"Se registró la persona con RUT {user.rut}",
            usuario_accion=usuario_accion
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al registrar la persona con RUT %s",
            user.rut
        )

        raise HTTPException(
            status_code=500,
            detail="Error al registrar la persona"
        )

    return {
        "status": "success",
        "message": "Persona creada exitosamente tras validación de cédula."
    }


def list_users(db):

    try:

        return obtener_personas(db)

    except Exception:

        logger.exception("Error al obtener personas")

        raise HTTPException(
            status_code=500,
            detail="Error al obtener personas"
        )


def update_user(db, id_persona, user, usuario_accion="admin"):

    try:

        filas = update_user_repository(
            db,
            id_persona,
            user
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        registrar_auditoria(
            db,
            tabla_afectada="persona",
            accion_realizada="UPDATE",
            descripcion=f"Se actualizó la persona ID {id_persona}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "mensaje": "Usuario actualizado correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al actualizar el usuario %s",
            id_persona
        )

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar usuario"
        )


def delete_user(db, id_persona, usuario_accion="admin"):

    try:

        filas = delete_user_repository(db, id_persona)

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        registrar_auditoria(
            db,
            tabla_afectada="persona",
            accion_realizada="DELETE",
            descripcion=f"Se eliminó la persona ID {id_persona}",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "mensaje": "Usuario eliminado correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al eliminar el usuario %s",
            id_persona
        )

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar usuario"
        )


def update_estado_persona(
    db,
    id_persona: int,
    estado: str,
    usuario_accion="admin"
):

    try:

        if estado not in ["activo", "inactivo"]:

            raise HTTPException(
                status_code=400,
                detail="Estado inválido"
            )

        filas = update_estado_persona_repository(
            db,
            id_persona,
            estado
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        registrar_auditoria(
            db,
            tabla_afectada="persona",
            accion_realizada="UPDATE",
            descripcion=f"Se cambió el estado de la persona ID {id_persona} a '{estado}'",
            usuario_accion=usuario_accion
        )

        db.commit()

        return {
            "mensaje": f"Persona {estado} correctamente"
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:

        db.rollback()

        logger.exception(
            "Error al cambiar el estado de la persona %s",
            id_persona
        )

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar estado"
        )
