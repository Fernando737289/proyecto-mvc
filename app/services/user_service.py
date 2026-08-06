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

async def create_user(user):

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

    if existe_usuario_por_rut(user.rut):

        raise HTTPException(
            status_code=400,
            detail="Ya existe una persona registrada con ese RUT"
        )

    serial_encriptado = encrypt_data(
        user.serial_number
    )

    insertar_usuario(
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

    return {
        "status": "success",
        "message": "Persona creada exitosamente tras validación de cédula."
    }

def list_users():

    try:

        return obtener_personas()

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al obtener personas"
        )

    
def update_user(id_persona, user):

    try:

        filas = update_user_repository(
            id_persona,
            user
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        return {
            "mensaje": "Usuario actualizado correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar usuario"
        )
     
def delete_user(id_persona):

    try:

        filas = delete_user_repository(id_persona)

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Usuario no encontrado"
            )

        return {
            "mensaje": "Usuario eliminado correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar usuario"
        )

    
def update_estado_persona(
    id_persona: int,
    estado: str
):

    try:

        if estado not in ["activo", "inactivo"]:

            raise HTTPException(
                status_code=400,
                detail="Estado inválido"
            )

        filas = update_estado_persona_repository(
            id_persona,
            estado
        )

        if filas == 0:

            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        return {
            "mensaje": f"Persona {estado} correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar estado"
        )