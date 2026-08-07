from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Validación de RUT chileno
# ---------------------------------------------------------------------------

def normalizar_rut(rut: str) -> str:
    return rut.upper().replace(".", "").strip()


def _calcular_dv(cuerpo: str) -> str:
    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    dv = 11 - resto
    if dv == 11:
        return "0"
    if dv == 10:
        return "K"
    return str(dv)


def validar_rut(rut: str) -> str:
    rut = normalizar_rut(rut)
    if not rut:
        raise ValueError("El RUT es obligatorio")

    if "-" in rut:
        cuerpo, dv = rut.split("-", 1)
    else:
        if len(rut) <= 1:
            raise ValueError("RUT inválido")
        cuerpo, dv = rut[:-1], rut[-1]

    if not cuerpo.isdigit() or dv not in "0123456789K":
        raise ValueError("Formato de RUT inválido")

    if _calcular_dv(cuerpo) != dv:
        raise ValueError("El dígito verificador del RUT es inválido")

    return f"{cuerpo}-{dv}"


# ---------------------------------------------------------------------------
# Respuestas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Personas
# ---------------------------------------------------------------------------

class UserCreate(ORMModel):

    rut: str
    serial_number: str

    nombres: str = Field(min_length=2, max_length=100)
    apellidos: str = Field(min_length=2, max_length=100)

    direccion: str | None = Field(default=None, max_length=200)
    numero_direccion: str | None = Field(default=None, max_length=10)
    telefono: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    fecha_nacimiento: date | None = None

    @field_validator("rut")
    @classmethod
    def _validar_rut(cls, v: str) -> str:
        return validar_rut(v)

    @field_validator("serial_number")
    @classmethod
    def _serial_number_no_vacio(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El número de serie es obligatorio")
        return v


class UpdateEstadoPersonaRequest(BaseModel):

    estado: Literal["activo", "inactivo"]


# ---------------------------------------------------------------------------
# Autenticación y usuarios de la plataforma
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):

    email: EmailStr
    password: str


class CreateUsuarioRequest(BaseModel):

    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$"
    )
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# ---------------------------------------------------------------------------
# Beneficios
# ---------------------------------------------------------------------------

class BeneficioCreate(BaseModel):

    nombre: str = Field(min_length=3, max_length=150)
    descripcion: str | None = None
    tipo_descuento: str = Field(max_length=50)
    valor_descuento: float = Field(ge=0)
    stock: int = Field(ge=0)
    fecha_inicio: date
    fecha_vencimiento: date
    comercio: str | None = Field(default=None, max_length=150)

    @field_validator("fecha_vencimiento")
    @classmethod
    def _fecha_vencimiento_posterior(cls, v: date, info) -> date:
        fecha_inicio = info.data.get("fecha_inicio")
        if fecha_inicio and v < fecha_inicio:
            raise ValueError(
                "La fecha de vencimiento debe ser posterior a la fecha de inicio"
            )
        return v


# ---------------------------------------------------------------------------
# Tarjetas
# ---------------------------------------------------------------------------

class CreateTarjetaRequest(BaseModel):

    rut: str
    nombres: str = Field(min_length=2)
    apellidos: str = Field(min_length=2)
    telefono: str | None = Field(default=None, max_length=20)

    @field_validator("rut")
    @classmethod
    def _validar_rut(cls, v: str) -> str:
        return validar_rut(v)


class UpdateTarjetaRequest(BaseModel):

    estado: Literal["activa", "bloqueada", "vencida"]
    fecha_vencimiento: date


# ---------------------------------------------------------------------------
# QR y verificación de cédula
# ---------------------------------------------------------------------------

class QRRequest(BaseModel):

    rut: str

    @field_validator("rut")
    @classmethod
    def _validar_rut(cls, v: str) -> str:
        return validar_rut(v)


class QRResponse(BaseModel):

    codigo_qr: str


class VerificacionCedulaSchema(BaseModel):

    user_rut: str
    serial_number: str = Field(min_length=1)

    @field_validator("user_rut")
    @classmethod
    def _validar_rut(cls, v: str) -> str:
        return validar_rut(v)
