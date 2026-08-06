from sqlalchemy import (
    DECIMAL,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Persona(Base):
    __tablename__ = "persona"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    rut = Column(String(12), nullable=False, unique=True)
    serial_number = Column(String(500), nullable=False)
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    direccion = Column(String(200))
    numero_direccion = Column(String(10))
    telefono = Column(String(20))
    email = Column(String(100))
    fecha_nacimiento = Column(Date)
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, server_default=func.current_timestamp())

    tarjeta = relationship("Tarjeta", back_populates="persona", uselist=False)
    historiales = relationship("HistorialBeneficio", back_populates="persona")


class Tarjeta(Base):
    __tablename__ = "tarjeta"

    id_tarjeta = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(
        Integer,
        ForeignKey("persona.id_persona"),
        nullable=False,
        unique=True
    )
    numero_tarjeta = Column(String(50), nullable=False, unique=True)
    codigo_qr = Column(Text, nullable=False)
    fecha_emision = Column(Date, nullable=False)
    fecha_vencimiento = Column(Date, nullable=False)
    estado = Column(String(20), nullable=False, default="activa")

    persona = relationship("Persona", back_populates="tarjeta")


class Beneficio(Base):
    __tablename__ = "beneficios"

    id_beneficio = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    tipo_descuento = Column(String(50))
    valor_descuento = Column(DECIMAL(10, 2))
    stock = Column(Integer, nullable=False, default=0)
    fecha_inicio = Column(Date)
    fecha_vencimiento = Column(Date)
    comercio = Column(String(150))
    estado = Column(String(20), nullable=False, default="activo")

    historiales = relationship("HistorialBeneficio", back_populates="beneficio")


class HistorialBeneficio(Base):
    __tablename__ = "historial_beneficios"

    id_historial = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(
        Integer,
        ForeignKey("persona.id_persona"),
        nullable=False
    )
    id_beneficio = Column(
        Integer,
        ForeignKey("beneficios.id_beneficio"),
        nullable=False
    )
    codigo_canje = Column(String(50), nullable=False)
    fecha_uso = Column(DateTime, server_default=func.current_timestamp())

    persona = relationship("Persona", back_populates="historiales")
    beneficio = relationship("Beneficio", back_populates="historiales")


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False, default="funcionario")
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, server_default=func.current_timestamp())
    email = Column(String(255), nullable=False)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria = Column(Integer, primary_key=True, autoincrement=True)
    tabla_afectada = Column(String(100))
    accion_realizada = Column(String(50))
    descripcion = Column(Text)
    usuario_accion = Column(String(100))
    fecha_accion = Column(DateTime, server_default=func.current_timestamp())
