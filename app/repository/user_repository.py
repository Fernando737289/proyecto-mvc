from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Persona


def existe_usuario_por_rut(db: Session, rut: str):

    return db.execute(
        select(Persona.id_persona).where(Persona.rut == rut)
    ).scalar_one_or_none()


def insertar_usuario(
    db: Session,
    rut,
    serial_number,
    nombres,
    apellidos,
    direccion,
    numero_direccion,
    telefono,
    email,
    fecha_nacimiento
):

    persona = Persona(
        rut=rut,
        serial_number=serial_number,
        nombres=nombres,
        apellidos=apellidos,
        direccion=direccion,
        numero_direccion=numero_direccion,
        telefono=telefono,
        email=email,
        fecha_nacimiento=fecha_nacimiento
    )

    db.add(persona)

    return persona


def obtener_personas(db: Session):

    return db.execute(
        select(Persona)
    ).scalars().all()


def update_user_repository(db: Session, id_persona, user):

    persona = db.get(Persona, id_persona)

    if not persona:
        return 0

    persona.rut = user.rut
    persona.nombres = user.nombres
    persona.apellidos = user.apellidos
    persona.direccion = user.direccion
    persona.numero_direccion = user.numero_direccion
    persona.telefono = user.telefono
    persona.email = user.email
    persona.fecha_nacimiento = user.fecha_nacimiento

    return 1


def delete_user_repository(db: Session, id_persona):

    persona = db.get(Persona, id_persona)

    if not persona:
        return 0

    db.delete(persona)

    return 1


def update_estado_persona_repository(
    db: Session,
    id_persona,
    estado
):

    persona = db.get(Persona, id_persona)

    if not persona:
        return 0

    persona.estado = estado

    return 1
