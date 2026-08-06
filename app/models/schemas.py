from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PersonaOut(ORMModel):

    id_persona: int
    rut: str
    nombres: str
    apellidos: str
    direccion: str | None = None
    numero_direccion: str | None = None
    telefono: str | None = None
    email: str | None = None
    fecha_nacimiento: date | None = None
    estado: str
    fecha_creacion: datetime | None = None


class TarjetaOut(BaseModel):

    id_persona: int
    nombres: str
    apellidos: str
    rut: str
    numero_tarjeta: str
    codigo_qr: str
    vigencia: date
    estado: str


class BeneficioOut(ORMModel):

    id_beneficio: int
    nombre: str
    descripcion: str | None = None
    tipo_descuento: str | None = None
    valor_descuento: float | None = None
    stock: int
    fecha_inicio: date | None = None
    fecha_vencimiento: date | None = None
    comercio: str | None = None
    estado: str


class HistorialOut(BaseModel):

    beneficio: str
    fecha_uso: datetime
    codigo_canje: str
    descuento: float | None = None
    comercio: str | None = None


class AuditoriaOut(ORMModel):

    tabla_afectada: str | None = None
    accion_realizada: str | None = None
    descripcion: str | None = None
    usuario_accion: str | None = None
    fecha_accion: datetime | None = None
