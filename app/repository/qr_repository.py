from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Persona


def get_persona_by_rut(db: Session, rut: str):

    return db.execute(
        select(Persona).where(Persona.rut == rut)
    ).scalar_one_or_none()
