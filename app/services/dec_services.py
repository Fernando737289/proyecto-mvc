import os
import httpx
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()

URL_DEC = os.getenv("URL_API")
DEC_API_KEY = os.getenv("DEC_API_KEY")

async def validar_vigencia_rut(user_rut: str, serial_number: str, api_key: str = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key if api_key is not None else DEC_API_KEY
    }
    
    payload = {
        "user_rut": user_rut,
        "serial_number": serial_number
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(URL_DEC, headers=headers, json=payload, timeout=10.0)
            
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error en el servicio externo de validación: {e.response.text}"
            )
        except httpx.RequestError:
            
            raise HTTPException(
                status_code=status.HTTP_500_SERVICE_UNAVAILABLE,
                detail="El servicio externo de validación no se encuentra disponible temporalmente."
            )