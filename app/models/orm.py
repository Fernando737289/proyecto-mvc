from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Persona(Base):
    __tablename__ = "persona"
    __table_args__ = (
        UniqueConstraint("rut", name="uk_persona_rut"),
    )

    id_persona: Mapped[int] = mapped_column(Integer, primary_key=True)
    rut: Mapped[str] = mapped_column(String(12), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(500), nullable=False)
    nombres: Mapped[str] = mapped_column(String(100), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(100), nullable=False)
    direccion: Mapped[str | None] = mapped_column(String(200))
    numero_direccion: Mapped[str | None] = mapped_column(String(10))
    telefono: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(100))
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo"),
        nullable=False,
        default="activo",
        server_default="activo",
    )
    fecha_creacion: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    tarjeta: Mapped["Tarjeta | None"] = relationship(
        back_populates="persona", uselist=False
    )
    historiales: Mapped[list["HistorialBeneficio"]] = relationship(
        back_populates="persona"
    )


class Tarjeta(Base):
    __tablename__ = "tarjeta"
    __table_args__ = (
        UniqueConstraint("id_persona", name="uk_tarjeta_persona"),
        UniqueConstraint("numero_tarjeta", name="uk_tarjeta_numero"),
    )

    id_tarjeta: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_persona: Mapped[int] = mapped_column(
        ForeignKey(
            "persona.id_persona",
            name="fk_tarjeta_persona",
            ondelete="RESTRICT",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    numero_tarjeta: Mapped[str] = mapped_column(String(50), nullable=False)
    codigo_qr: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    fecha_emision: Mapped[date] = mapped_column(Date, nullable=False)
    fecha_vencimiento: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(
        Enum("activa", "bloqueada", "vencida"),
        nullable=False,
        default="activa",
        server_default="activa",
    )

    persona: Mapped["Persona"] = relationship(back_populates="tarjeta")


class Beneficio(Base):
    __tablename__ = "beneficios"

    id_beneficio: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    tipo_descuento: Mapped[str | None] = mapped_column(
        Enum("porcentaje", "monto_fijo", "2x1")
    )
    valor_descuento: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    stock: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date)
    comercio: Mapped[str | None] = mapped_column(String(150))
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo"),
        nullable=False,
        default="activo",
        server_default="activo",
    )

    historiales: Mapped[list["HistorialBeneficio"]] = relationship(
        back_populates="beneficio"
    )


class HistorialBeneficio(Base):
    __tablename__ = "historial_beneficios"

    id_historial: Mapped[int] = mapped_column(Integer, primary_key=True)
    id_persona: Mapped[int] = mapped_column(
        ForeignKey("persona.id_persona", name="fk_historial_persona"),
        nullable=False,
    )
    id_beneficio: Mapped[int] = mapped_column(
        ForeignKey("beneficios.id_beneficio", name="fk_historial_beneficio"),
        nullable=False,
    )
    codigo_canje: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha_uso: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    persona: Mapped["Persona"] = relationship(back_populates="historiales")
    beneficio: Mapped["Beneficio"] = relationship(back_populates="historiales")


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (
        UniqueConstraint("username", name="uk_usuario_username"),
        UniqueConstraint("email", name="uk_usuario_email"),
    )

    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(
        Enum("admin", "funcionario"),
        nullable=False,
        default="funcionario",
        server_default="funcionario",
    )
    estado: Mapped[str] = mapped_column(
        Enum("activo", "inactivo"),
        nullable=False,
        default="activo",
        server_default="activo",
    )
    fecha_creacion: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)


class Auditoria(Base):
    __tablename__ = "auditoria"

    id_auditoria: Mapped[int] = mapped_column(Integer, primary_key=True)
    tabla_afectada: Mapped[str | None] = mapped_column(String(100))
    accion_realizada: Mapped[str | None] = mapped_column(String(50))
    descripcion: Mapped[str | None] = mapped_column(Text)
    usuario_accion: Mapped[str | None] = mapped_column(String(100))
    fecha_accion: Mapped[datetime | None] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
