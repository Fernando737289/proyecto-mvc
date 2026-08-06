from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.orm import Persona


def get_persona_by_rut(rut: str):

    session = SessionLocal()

    try:

        return session.execute(
            select(Persona).where(Persona.rut == rut)
        ).scalar_one_or_none()

    finally:
        session.close()
