import os
from pathlib import Path

os.environ["DB_NAME"] = "backTarjetaVecino_test"

from datetime import date, timedelta

import mysql.connector
import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.orm import Beneficio, Persona, Tarjeta, Usuario

import main as main_app_module

TEST_DB = "backTarjetaVecino_test"
ROOT = Path(__file__).resolve().parent.parent

ADMIN_PASSWORD = "AdminClave123"
FUNCIONARIO_PASSWORD = "Funcionario123"


def _crear_usuario_en_bd(username, email, rol, password):
    with SessionLocal() as db:
        usuario = Usuario(
            username=username,
            email=email,
            password_hash=hash_password(password),
            rol=rol,
            estado="activo",
        )
        db.add(usuario)
        db.commit()


def _crear_persona_en_bd(
    rut="14187947-2",
    nombres="Francisco",
    apellidos="Baez",
    telefono=None,
    estado="activo",
):
    with SessionLocal() as db:
        persona = Persona(
            rut=rut,
            serial_number="test-serial",
            nombres=nombres,
            apellidos=apellidos,
            telefono=telefono,
            estado=estado,
        )
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona.id_persona


def _crear_beneficio_en_bd(nombre="Descuento Test", stock=10):
    with SessionLocal() as db:
        beneficio = Beneficio(
            nombre=nombre,
            tipo_descuento="monto_fijo",
            valor_descuento=1000,
            stock=stock,
            estado="activo",
        )
        db.add(beneficio)
        db.commit()
        db.refresh(beneficio)
        return beneficio.id_beneficio


def _crear_tarjeta_en_bd(
    id_persona,
    numero_tarjeta="123456",
    codigo_qr="qr-anterior",
    estado="activa",
):
    with SessionLocal() as db:
        tarjeta = Tarjeta(
            id_persona=id_persona,
            numero_tarjeta=numero_tarjeta,
            codigo_qr=codigo_qr,
            fecha_emision=date.today(),
            fecha_vencimiento=date.today() + timedelta(days=365),
            estado=estado,
        )
        db.add(tarjeta)
        db.commit()
        db.refresh(tarjeta)
        return tarjeta.id_tarjeta


@pytest.fixture(scope="session", autouse=True)
def prepared_db():
    conexion = mysql.connector.connect(
        host=settings.DB_HOST,
        port=int(settings.DB_PORT),
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
    )
    cursor = conexion.cursor()
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {TEST_DB} "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    conexion.commit()
    cursor.close()
    conexion.close()

    command.upgrade(Config(ROOT / "alembic.ini"), "head")

    yield


@pytest.fixture(autouse=True)
def _tablas_vacias(prepared_db):
    with engine.begin() as conexion:
        conexion.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for tabla in Base.metadata.sorted_tables:
            conexion.execute(text(f"TRUNCATE TABLE {tabla.name}"))
        conexion.execute(text("SET FOREIGN_KEY_CHECKS=1"))
    yield


@pytest.fixture(autouse=True)
def _sin_rate_limit():
    from app.routers.auth_router import limiter

    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture()
def client():
    with TestClient(main_app_module.app) as test_client:
        yield test_client


@pytest.fixture()
def admin_token(client):
    _crear_usuario_en_bd(
        "admin_test", "admin_test@example.cl", "admin", ADMIN_PASSWORD
    )
    respuesta = client.post(
        "/auth/login",
        json={"email": "admin_test@example.cl", "password": ADMIN_PASSWORD},
    )
    assert respuesta.status_code == 200
    return respuesta.json()["access_token"]


@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture()
def funcionario_headers(client):
    _crear_usuario_en_bd(
        "funcionario_test",
        "funcionario_test@example.cl",
        "funcionario",
        FUNCIONARIO_PASSWORD,
    )
    respuesta = client.post(
        "/auth/login",
        json={
            "email": "funcionario_test@example.cl",
            "password": FUNCIONARIO_PASSWORD,
        },
    )
    assert respuesta.status_code == 200
    return {"Authorization": f"Bearer {respuesta.json()['access_token']}"}


@pytest.fixture()
def dec_valida(monkeypatch):
    async def fake_validar(user_rut, serial_number, api_key=None):
        return {"status": 200, "result": {"Verificacion": "V", "Glosa": "Vigente"}}

    monkeypatch.setattr(
        "app.services.user_service.validar_vigencia_rut", fake_validar
    )
    return fake_validar


@pytest.fixture()
def dec_no_vigente(monkeypatch):
    async def fake_validar(user_rut, serial_number, api_key=None):
        return {"status": 200, "result": {"Verificacion": "N", "Glosa": "No vigente"}}

    monkeypatch.setattr(
        "app.services.user_service.validar_vigencia_rut", fake_validar
    )
    return fake_validar


@pytest.fixture()
def crear_persona():
    return _crear_persona_en_bd


@pytest.fixture()
def crear_beneficio():
    return _crear_beneficio_en_bd
