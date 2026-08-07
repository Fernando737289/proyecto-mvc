from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Beneficio


def crear_beneficio(db: Session, data):

    beneficio = Beneficio(
        nombre=data.nombre,
        descripcion=data.descripcion,
        tipo_descuento=data.tipo_descuento,
        valor_descuento=data.valor_descuento,
        stock=data.stock,
        fecha_inicio=data.fecha_inicio,
        fecha_vencimiento=data.fecha_vencimiento,
        comercio=data.comercio
    )

    db.add(beneficio)
    db.flush()

    return beneficio.id_beneficio


def obtener_beneficios(db: Session):

    return db.execute(
        select(Beneficio).where(Beneficio.estado == "activo")
    ).scalars().all()


def eliminar_beneficio(db: Session, id_beneficio: int):

    beneficio = db.get(Beneficio, id_beneficio)

    if not beneficio:
        return 0

    beneficio.estado = "inactivo"

    return 1


def actualizar_beneficio(
    db: Session,
    id_beneficio: int,
    data
):

    beneficio = db.get(Beneficio, id_beneficio)

    if not beneficio:
        return 0

    beneficio.nombre = data.nombre
    beneficio.descripcion = data.descripcion

    return 1
