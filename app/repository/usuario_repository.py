from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.orm import Usuario


def buscar_usuario_por_username_email(
    db: Session,
    username: str,
    email: str
):

    return db.execute(
        select(Usuario).where(
            or_(
                Usuario.username == username,
                Usuario.email == email
            )
        )
    ).scalar_one_or_none()


def crear_usuario(
    db: Session,
    username: str,
    email: str,
    password: str
):

    usuario = Usuario(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )

    db.add(usuario)
    db.flush()

    return usuario.id_usuario
