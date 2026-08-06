from fastapi import HTTPException
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.generador_codigo import generar_codigo_canje
from app.models.orm import Beneficio, HistorialBeneficio, Persona


def canjear_beneficio(
    id_persona: int,
    id_beneficio: int
):

    session = SessionLocal()

    try:

        persona = session.get(Persona, id_persona)

        if not persona:
            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        beneficio = session.get(Beneficio, id_beneficio)

        if not beneficio:
            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        if beneficio.stock <= 0:
            raise HTTPException(
                status_code=400,
                detail="Beneficio sin stock"
            )

        canje_existente = session.execute(
            select(HistorialBeneficio.id_historial).where(
                HistorialBeneficio.id_persona == id_persona,
                HistorialBeneficio.id_beneficio == id_beneficio
            )
        ).scalar_one_or_none()

        if canje_existente:
            raise HTTPException(
                status_code=400,
                detail="Este beneficio ya fue canjeado por esta persona"
            )

        beneficio.stock -= 1

        codigo_canje = generar_codigo_canje()

        session.add(HistorialBeneficio(
            id_persona=id_persona,
            id_beneficio=id_beneficio,
            codigo_canje=codigo_canje
        ))

        session.commit()

        return {
            "mensaje": "Beneficio canjeado correctamente"
        }

    except HTTPException:
        session.rollback()
        raise

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        session.close()
