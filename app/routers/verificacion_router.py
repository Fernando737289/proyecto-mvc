from fastapi import APIRouter, HTTPException, status
from app.services.dec_services import validar_vigencia_rut
from app.models.schemas import VerificacionCedulaSchema

router = APIRouter(
    prefix="/verificaciones",
    tags=["Verificación de Cédula"]
)

@router.post("/validar-cedula")
async def validar_cedula(payload: VerificacionCedulaSchema):
     
    resultado = await validar_vigencia_rut(
        user_rut=payload.user_rut, 
        serial_number=payload.serial_number
        
    )
    
    if not resultado or resultado.get("status") != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.get("message", "No se pudo completar la verificación.")
        )
        
    result_data = resultado.get("result", {})
    
    return {
        "valido": result_data.get("Verificacion") == "V",
        "detalle": result_data.get("Glosa"),
        "datos_completos": result_data
    }