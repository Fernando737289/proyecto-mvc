from fastapi import HTTPException

from app.repository.outh_repository import (
    buscar_usuario_por_username_email,
    crear_usuario
)

def create_usuario(data):

    try:

        usuario = buscar_usuario_por_username_email(
            data.username,
            data.email
        )

        if usuario:

            raise HTTPException(
                status_code=400,
                detail="Usuario o correo ya registrado"
            )

        id_usuario = crear_usuario(
            data.username,
            data.email,
            data.password
        )

        return {
            "id_usuario": id_usuario,
            "mensaje": "Usuario creado correctamente"
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )