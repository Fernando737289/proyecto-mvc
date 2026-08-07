from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.orm import HistorialBeneficio, Persona


def existe_persona(db: Session, id_persona: int) -> bool:

    return db.get(Persona, id_persona) is not None


def obtener_historial_persona(db: Session, id_persona: int):

    stmt = (
        select(HistorialBeneficio)
        .options(joinedload(HistorialBeneficio.beneficio))
        .where(HistorialBeneficio.id_persona == id_persona)
        .order_by(HistorialBeneficio.fecha_uso.desc())
    )

    return db.execute(stmt).scalars().all()
