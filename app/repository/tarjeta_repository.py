from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import SessionLocal
from app.models.orm import Persona, Tarjeta


def verificar_tarjeta_existente(id_persona: int):

    session = SessionLocal()

    try:

        return session.execute(
            select(Tarjeta.id_tarjeta).where(Tarjeta.id_persona == id_persona)
        ).scalar_one_or_none()

    finally:
        session.close()


def crear_tarjeta(
    id_persona: int,
    numero_tarjeta: str,
    codigo_qr: str,
    fecha_emision,
    fecha_vencimiento,
    estado: str
):

    session = SessionLocal()

    try:

        tarjeta = Tarjeta(
            id_persona=id_persona,
            numero_tarjeta=numero_tarjeta,
            codigo_qr=codigo_qr,
            fecha_emision=fecha_emision,
            fecha_vencimiento=fecha_vencimiento,
            estado=estado
        )

        session.add(tarjeta)
        session.commit()

        return tarjeta.id_tarjeta

    finally:
        session.close()


def get_tarjeta(rut=None, numero_tarjeta=None):

    session = SessionLocal()

    try:

        stmt = (
            select(Tarjeta)
            .join(Persona, Tarjeta.id_persona == Persona.id_persona)
            .options(joinedload(Tarjeta.persona))
        )

        if rut:
            stmt = stmt.where(Persona.rut == rut)

        if numero_tarjeta:
            stmt = stmt.where(Tarjeta.numero_tarjeta == numero_tarjeta)

        return session.execute(stmt).scalars().first()

    finally:
        session.close()


def get_tarjeta_by_id(id_tarjeta):

    session = SessionLocal()

    try:

        return session.get(Tarjeta, id_tarjeta)

    finally:
        session.close()


def update_tarjeta(
    id_tarjeta,
    estado,
    fecha_vencimiento
):

    session = SessionLocal()

    try:

        tarjeta = session.get(Tarjeta, id_tarjeta)

        if not tarjeta:
            return 0

        tarjeta.estado = estado
        tarjeta.fecha_vencimiento = fecha_vencimiento

        session.commit()

        return 1

    finally:
        session.close()


def obtener_tarjeta_por_id(id_tarjeta: int):

    session = SessionLocal()

    try:

        return session.get(Tarjeta, id_tarjeta)

    finally:
        session.close()


def eliminar_tarjeta(id_tarjeta: int):

    session = SessionLocal()

    try:

        tarjeta = session.get(Tarjeta, id_tarjeta)

        if not tarjeta:
            return 0

        session.delete(tarjeta)
        session.commit()

        return 1

    finally:
        session.close()
