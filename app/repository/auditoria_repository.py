from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.orm import Auditoria


def insertar_auditoria(
    db: Session,
    tabla_afectada: str,
    accion_realizada: str,
    descripcion: str,
    usuario_accion: str
):

    db.add(Auditoria(
        tabla_afectada=tabla_afectada,
        accion_realizada=accion_realizada,
        descripcion=descripcion,
        usuario_accion=usuario_accion
    ))


def obtener_auditoria(db: Session):

    return db.execute(
        select(Auditoria).order_by(Auditoria.fecha_accion.desc())
    ).scalars().all()
