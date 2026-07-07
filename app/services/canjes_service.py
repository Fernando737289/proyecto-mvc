from fastapi import HTTPException
from app.core.generador_codigo import generar_codigo_canje

from app.repository.canje_repository import (
    obtener_persona,
    obtener_beneficio,
    obtener_canje_existente,
    descontar_stock,
    registrar_canje,
    obtener_conexion
)

def canjear_beneficio(
    id_persona: int,
    id_beneficio: int
):
    conexion, cursor = obtener_conexion()

    
    try:
        
        persona = obtener_persona(cursor, id_persona)


        if not persona:
            raise HTTPException(
                status_code=404,
                detail="Persona no encontrada"
            )

        beneficio = obtener_beneficio(
            cursor,
            id_beneficio
        )

        if not beneficio:
            raise HTTPException(
                status_code=404,
                detail="Beneficio no encontrado"
            )

        if beneficio["stock"] <= 0:
            raise HTTPException(
                status_code=400,
                detail="Beneficio sin stock"
            )

        canje_existente = obtener_canje_existente(
            cursor,
            persona["id_persona"],
            id_beneficio
        )

        if canje_existente:
            raise HTTPException(
                status_code=400,
                detail="Este beneficio ya fue canjeado por esta persona"
            )

        descontar_stock(
            cursor,
            id_beneficio
        )

        codigo_canje = generar_codigo_canje()

        registrar_canje(
            cursor,
            persona["id_persona"],
            id_beneficio,
            codigo_canje
        )

        conexion.commit()

        return {
            "mensaje": "Beneficio canjeado correctamente"
        }

    except HTTPException:
        conexion.rollback()
        raise

    except Exception as e:
        
        conexion.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        cursor.close()
        conexion.close()