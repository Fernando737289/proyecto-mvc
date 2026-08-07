from fastapi import HTTPException

from app.core.security import (
    verify_password,
    create_access_token
)

from app.repository.auth_repository import obtener_usuario_por_email


def login_user(db, email: str, password: str):

    usuario = obtener_usuario_por_email(db, email)

    if not usuario:
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    if usuario.estado != "activo":
        raise HTTPException(
            status_code=401,
            detail="Usuario inactivo"
        )

    if not verify_password(password, usuario.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Credenciales inválidas"
        )

    token = create_access_token({
        "sub": usuario.username,
        "id_usuario": usuario.id_usuario,
        "rol": usuario.rol
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }
