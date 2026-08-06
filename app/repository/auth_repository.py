from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.orm import Usuario


def obtener_usuario_por_email(email: str):

    session = SessionLocal()

    try:

        return session.execute(
            select(Usuario).where(Usuario.email == email)
        ).scalar_one_or_none()

    finally:
        session.close()
