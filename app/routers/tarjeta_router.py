from fastapi import APIRouter, Depends
from app.models.tarjeta_model import CreateTarjetaRequest, UpdateTarjetaRequest
from app.models.schemas import TarjetaOut
from app.services.tarjeta_service import (
    create_tarjeta,
    get_tarjeta,
    update_tarjeta,
    delete_tarjeta
)
from app.services.auditoria_service import registrar_auditoria
from app.core.dependencies import require_admin

router = APIRouter(
    prefix="/tarjeta",
    tags=["Tarjeta"]
)

@router.post("/crear")
def crear_tarjeta(
    data: CreateTarjetaRequest,
    admin=Depends(require_admin)
):

    resultado = create_tarjeta(
        data.rut,
        data.nombres,
        data.apellidos,
        data.telefono
    )

    registrar_auditoria(
        tabla_afectada="tarjeta",
        accion_realizada="INSERT",
        descripcion=f"Se creó una tarjeta para el RUT {data.rut}",
        usuario_accion=admin["sub"]
    )

    return resultado

@router.get("/buscar", response_model=TarjetaOut)
def obtener_tarjeta(
    rut: str | None = None,
    numero_tarjeta: str | None = None
):

    return get_tarjeta(
        rut=rut,
        numero_tarjeta=numero_tarjeta
    )

@router.put("/{id_tarjeta}")
def actualizar_tarjeta(
    id_tarjeta: int,
    data: UpdateTarjetaRequest,
    admin=Depends(require_admin)
):

    resultado = update_tarjeta(
        id_tarjeta,
        data.estado,
        data.fecha_vencimiento
    )

    registrar_auditoria(
        tabla_afectada="tarjeta",
        accion_realizada="UPDATE",
        descripcion=f"Se actualizó la tarjeta ID {id_tarjeta}",
        usuario_accion=admin["sub"]
    )

    return resultado

@router.delete("/{id_tarjeta}")
def eliminar_tarjeta(
    id_tarjeta: int,
    admin=Depends(require_admin)
):

    resultado = delete_tarjeta(id_tarjeta)

    registrar_auditoria(
        tabla_afectada="tarjeta",
        accion_realizada="DELETE",
        descripcion=f"Se eliminó la tarjeta ID {id_tarjeta}",
        usuario_accion=admin["sub"]
    )

    return resultado