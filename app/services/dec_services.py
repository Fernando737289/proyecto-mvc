import logging

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

API_URL = settings.API_URL
API_TOKEN = settings.API_TOKEN


async def validar_vigencia_rut(user_rut: str, serial_number: str, api_key: str | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key if api_key is not None else API_TOKEN
    }

    payload = {
        "user_rut": user_rut,
        "serial_number": serial_number
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, headers=headers, json=payload, timeout=10.0)

            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:

            logger.error(
                "El servicio externo de validación respondió con estado %s: %s",
                e.response.status_code,
                e.response.text
            )

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="El servicio externo de validación no pudo completar la solicitud."
            )
        except httpx.HTTPError:

            logger.exception("El servicio externo de validación no está disponible")

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio externo de validación no se encuentra disponible temporalmente."
            )
