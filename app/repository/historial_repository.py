from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import SessionLocal
from app.models.orm import HistorialBeneficio


def obtener_historial_persona(id_persona: int):

    session = SessionLocal()

    try:

        stmt = (
            select(HistorialBeneficio)
            .options(joinedload(HistorialBeneficio.beneficio))
            .where(HistorialBeneficio.id_persona == id_persona)
            .order_by(HistorialBeneficio.fecha_uso.desc())
        )

        return session.execute(stmt).scalars().all()

    finally:
        session.close()
