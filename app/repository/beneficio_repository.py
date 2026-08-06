from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.orm import Beneficio


def crear_beneficio(data):

    session = SessionLocal()

    try:

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

        session.add(beneficio)
        session.commit()

        return beneficio.id_beneficio

    finally:
        session.close()


def obtener_beneficios():

    session = SessionLocal()

    try:

        return session.execute(
            select(Beneficio).where(Beneficio.estado == "activo")
        ).scalars().all()

    finally:
        session.close()


def eliminar_beneficio(id_beneficio: int):

    session = SessionLocal()

    try:

        beneficio = session.get(Beneficio, id_beneficio)

        if not beneficio:
            return 0

        beneficio.estado = "inactivo"

        session.commit()

        return 1

    finally:
        session.close()


def actualizar_beneficio(
    id_beneficio: int,
    data
):

    session = SessionLocal()

    try:

        beneficio = session.get(Beneficio, id_beneficio)

        if not beneficio:
            return 0

        beneficio.nombre = data.nombre
        beneficio.descripcion = data.descripcion

        session.commit()

        return 1

    finally:
        session.close()
