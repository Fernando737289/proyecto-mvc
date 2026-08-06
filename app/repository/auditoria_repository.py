from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.orm import Auditoria


def registrar_auditoria(
    tabla_afectada: str,
    accion_realizada: str,
    descripcion: str,
    usuario_accion: str
):

    session = SessionLocal()

    try:

        auditoria = Auditoria(
            tabla_afectada=tabla_afectada,
            accion_realizada=accion_realizada,
            descripcion=descripcion,
            usuario_accion=usuario_accion
        )

        session.add(auditoria)
        session.commit()

    finally:
        session.close()


def obtener_auditoria():

    session = SessionLocal()

    try:

        return session.execute(
            select(Auditoria).order_by(Auditoria.fecha_accion.desc())
        ).scalars().all()

    finally:
        session.close()
