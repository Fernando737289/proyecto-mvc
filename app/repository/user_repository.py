from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.orm import Persona


def existe_usuario_por_rut(rut: str):

    session = SessionLocal()

    try:

        return session.execute(
            select(Persona.id_persona).where(Persona.rut == rut)
        ).scalar_one_or_none()

    finally:
        session.close()


def insertar_usuario(
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

    session = SessionLocal()

    try:

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

        session.add(persona)
        session.commit()

    finally:
        session.close()


def obtener_personas():

    session = SessionLocal()

    try:

        return session.execute(
            select(Persona)
        ).scalars().all()

    finally:
        session.close()


def update_user_repository(id_persona, user):

    session = SessionLocal()

    try:

        persona = session.get(Persona, id_persona)

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

        session.commit()

        return 1

    finally:
        session.close()


def delete_user_repository(id_persona):

    session = SessionLocal()

    try:

        persona = session.get(Persona, id_persona)

        if not persona:
            return 0

        session.delete(persona)
        session.commit()

        return 1

    finally:
        session.close()


def update_estado_persona_repository(
    id_persona,
    estado
):

    session = SessionLocal()

    try:

        persona = session.get(Persona, id_persona)

        if not persona:
            return 0

        persona.estado = estado

        session.commit()

        return 1

    finally:
        session.close()
