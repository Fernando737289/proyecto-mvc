import random

from datetime import date, timedelta
from fastapi import HTTPException

from app.services.qr_service import (
    get_persona_by_rut,
    generar_qr
)
from app.repository.tarjeta_repository import (
    verificar_tarjeta_existente,
    crear_tarjeta,
    get_tarjeta,
    get_tarjeta_by_id,
    update_tarjeta,
    eliminar_tarjeta,
    obtener_tarjeta_por_id
)


def create_tarjeta(
    rut: str,
    nombres: str,
    apellidos: str,
    telefono: str | None = None
):

    try:

        persona = get_persona_by_rut(rut)

        if persona["nombres"].strip().lower() != nombres.strip().lower():
            raise HTTPException(
                status_code=400,
                detail="Los nombres no coinciden con los registros"
            )

        if persona["apellidos"].strip().lower() != apellidos.strip().lower():
            raise HTTPException(
                status_code=400,
                detail="Los apellidos no coinciden con los registros"
            )

        if telefono:

            telefono_bd = persona.get("telefono")

            if telefono_bd != telefono:
                raise HTTPException(
                    status_code=400,
                    detail="El teléfono no coincide con los registros"
                )

        tarjeta_existente = verificar_tarjeta_existente(
            persona["id_persona"]
        )

        if tarjeta_existente:
            raise HTTPException(
                status_code=400,
                detail="La persona ya posee una tarjeta"
            )

        codigo_qr = generar_qr(persona)

        numero_tarjeta = f"{random.randint(100000,999999)}"

        fecha_emision = date.today()

        fecha_vencimiento = fecha_emision + timedelta(days=365)

        id_tarjeta = crear_tarjeta(
            persona["id_persona"],
            numero_tarjeta,
            codigo_qr,
            fecha_emision,
            fecha_vencimiento,
            "activa"
        )

        return {
            "id_tarjeta": id_tarjeta,
            "numero_tarjeta": numero_tarjeta,
            "mensaje": "Tarjeta creada correctamente"
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al crear tarjeta: {str(e)}"
        )
        

def get_tarjeta(
    rut: str | None = None,
    numero_tarjeta: str | None = None
):

    try:

        if not rut and not numero_tarjeta:

            raise HTTPException(
                status_code=400,
                detail="Debe ingresar un rut o un número de tarjeta"
            )

        tarjeta = get_tarjeta(
            rut,
            numero_tarjeta
        )

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        return {
            "id_persona": tarjeta["id_persona"],
            "nombres": tarjeta["nombres"],
            "apellidos": tarjeta["apellidos"],
            "rut": tarjeta["rut"],
            "numero_tarjeta": tarjeta["numero_tarjeta"],
            "codigo_qr": tarjeta["codigo_qr"],
            "vigencia": tarjeta["fecha_vencimiento"],
            "estado": tarjeta["estado"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la tarjeta: {str(e)}"
        )

        
        
def update_tarjeta(
    id_tarjeta: int,
    estado: str,
    fecha_vencimiento
):

    try:

        tarjeta = get_tarjeta_by_id(
            id_tarjeta
        )

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        update_tarjeta(
            id_tarjeta,
            estado,
            fecha_vencimiento
        )

        return {
            "id_tarjeta": id_tarjeta,
            "mensaje": "Tarjeta actualizada correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al actualizar la tarjeta"
        )
        

def delete_tarjeta(id_tarjeta: int):

    try:

        tarjeta = obtener_tarjeta_por_id(id_tarjeta)

        if not tarjeta:

            raise HTTPException(
                status_code=404,
                detail="Tarjeta no encontrada"
            )

        eliminar_tarjeta(id_tarjeta)

        return {
            "id_tarjeta": id_tarjeta,
            "mensaje": "Tarjeta eliminada correctamente"
        }

    except HTTPException:
        raise

    except Exception:

        raise HTTPException(
            status_code=500,
            detail="Error al eliminar la tarjeta"
        )
