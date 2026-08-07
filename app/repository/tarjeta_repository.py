from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.orm import Persona, Tarjeta


def verificar_tarjeta_existente(db: Session, id_persona: int):

    return db.execute(
        select(Tarjeta.id_tarjeta).where(Tarjeta.id_persona == id_persona)
    ).scalar_one_or_none()


def crear_tarjeta(
    db: Session,
    id_persona: int,
    numero_tarjeta: str,
    codigo_qr: str,
    fecha_emision,
    fecha_vencimiento,
    estado: str
):

    tarjeta = Tarjeta(
        id_persona=id_persona,
        numero_tarjeta=numero_tarjeta,
        codigo_qr=codigo_qr,
        fecha_emision=fecha_emision,
        fecha_vencimiento=fecha_vencimiento,
        estado=estado
    )

    db.add(tarjeta)
    db.flush()

    return tarjeta.id_tarjeta


def get_tarjeta(db: Session, rut=None, numero_tarjeta=None):

    stmt = (
        select(Tarjeta)
        .join(Persona, Tarjeta.id_persona == Persona.id_persona)
        .options(joinedload(Tarjeta.persona))
    )

    if rut:
        stmt = stmt.where(Persona.rut == rut)

    if numero_tarjeta:
        stmt = stmt.where(Tarjeta.numero_tarjeta == numero_tarjeta)

    return db.execute(stmt).scalars().first()


def get_tarjeta_by_id(db: Session, id_tarjeta):

    return db.get(Tarjeta, id_tarjeta)


def actualizar_codigo_qr(db: Session, id_tarjeta: int, codigo_qr: str):

    tarjeta = db.get(Tarjeta, id_tarjeta)

    if not tarjeta:
        return 0

    tarjeta.codigo_qr = codigo_qr

    return 1


def update_tarjeta(
    db: Session,
    id_tarjeta,
    estado,
    fecha_vencimiento
):

    tarjeta = db.get(Tarjeta, id_tarjeta)

    if not tarjeta:
        return 0

    tarjeta.estado = estado
    tarjeta.fecha_vencimiento = fecha_vencimiento

    return 1


def obtener_tarjeta_por_id(db: Session, id_tarjeta: int):

    return db.get(Tarjeta, id_tarjeta)


def eliminar_tarjeta(db: Session, id_tarjeta: int):

    tarjeta = db.get(Tarjeta, id_tarjeta)

    if not tarjeta:
        return 0

    db.delete(tarjeta)

    return 1
