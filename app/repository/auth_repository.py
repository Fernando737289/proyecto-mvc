from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Usuario


def obtener_usuario_por_email(db: Session, email: str):

    return db.execute(
        select(Usuario).where(Usuario.email == email)
    ).scalar_one_or_none()
