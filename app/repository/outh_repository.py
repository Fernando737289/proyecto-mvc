from sqlalchemy import or_, select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.orm import Usuario


def buscar_usuario_por_username_email(
    username: str,
    email: str
):

    session = SessionLocal()

    try:

        return session.execute(
            select(Usuario).where(
                or_(
                    Usuario.username == username,
                    Usuario.email == email
                )
            )
        ).scalar_one_or_none()

    finally:
        session.close()


def crear_usuario(
    username: str,
    email: str,
    password: str
):

    session = SessionLocal()

    try:

        usuario = Usuario(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )

        session.add(usuario)
        session.commit()

        return usuario.id_usuario

    finally:
        session.close()
