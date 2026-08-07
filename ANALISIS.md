# Análisis del Proyecto: backend-TarjetaVecino

> Análisis técnico realizado como copiloto. No se modificó código; solo se creó este documento.

---

## 1. Resumen

Backend **FastAPI** para un sistema de tarjeta vecina municipal (San Bernardo): gestión de personas, tarjetas con QR, beneficios, canjes, validación contra el servicio externo DEC (vigencia de cédula), autenticación JWT y auditoría de operaciones.

- **Lenguaje:** Python 3.13
- **Framework:** FastAPI (asíncrono) + slowapi (rate limit) + CORS
- **Arquitectura:** MVC en capas `routers → services → repository → MySQL`
- **BD:** MySQL/MariaDB con SQL directo (`mysql-connector-python`), sin ORM activo (SQLAlchemy está en requirements pero no se usa)
- **Seguridad:** JWT (python-jose), bcrypt (passlib), cifrado Fernet para datos sensibles

---

## 2. Estructura de archivos

### Raíz

| Archivo | Descripción |
|---|---|
| `main.py` | Punto de entrada de FastAPI: crea la app, registra 10 routers, CORS y rate limiter |
| `requirements.txt` | Dependencias del proyecto |
| `README.md` | Instrucciones de instalación, configuración y ejecución |
| `backTarjetaVecino.sql` | Dump de BD: crea BD, 6 tablas, índices, FKs y datos semilla |
| `.gitignore` | Ignora `.env`, `.venv/`, `__pycache__/`, etc. |
| `.env` | **NO EXISTE** — requerido para arrancar |

### `app/`

| Capa | Archivos | Descripción |
|---|---|---|
| `core/` | `config.py`, `database.py`, `security.py`, `encryption.py`, `generador_codigo.py`, `dependencies.py` | Settings centralizados (pydantic-settings), conexión MySQL, hash/JWT, cifrado Fernet, códigos, dependencias de auth |
| `models/` | `orm.py`, `schemas.py` | Modelos ORM + **todos** los schemas de entrada/salida (consolidados, con validación de RUT) |
| `repository/` | `user`, `tarjeta`, `qr`, `beneficio`, `canje`, `historial`, `auditoria`, `auth`, `usuario` | Consultas SQL directas |
| `services/` | `user_service`, `tarjeta_service`, `qr_service`, `beneficio_service`, `canjes_service`, `historial_beneficio_service`, `auditoria_service`, `auth_service`, `usuario_service`, `db_service`, `dec_services` | Lógica de negocio y orquestación |
| `routers/` | 10 routers (21 endpoints) | Capa HTTP |

---

## 3. Endpoints por router

| Router | Prefijo | Métodos | Protección |
|---|---|---|---|
| `db_conection` | `/health` | GET `/test-db` | Pública |
| `auth_router` | `/auth` | POST `/login` (límite 5/min) | Pública |
| `usuario_router` (antes `Outh_router`) | `/auth` | POST `/registro` | Admin |
| `users` | `/users` | GET `/`, POST `/usuarios`, PUT `/{id}`, DELETE `/{id}`, PATCH `/{id}/estado` | CRUD admin (GET pública) |
| `qr_router` | (a definir) | POST `/generar` | — |
| `tarjeta_router` | `/tarjeta` | POST `/crear`, GET `/buscar`, PUT `/{id}`, DELETE `/{id}` | Admin (GET pública) |
| `beneficio_router` | `/beneficios` | POST `/crear`, GET `/`, PUT `/actualizar/{id}`, DELETE `/eliminar/{id}` | — |
| `canjes_router` | — | POST `/canjear`, GET `/historial/{id_persona}` | — |
| `verificacion_router` | `/verificaciones` | POST `/validar-cedula` | Pública (llama a DEC) |
| `auditoria_router` | — | GET `/` | — |

**Observación:** la protección por rol está verificada: `beneficio_router`, `tarjeta_router`, `users`, `usuario_router` y `qr_router` exigen `require_admin`; `canjes`/`historial` son públicos por diseño (kiosco vecino); `auditoria_router` exige `require_admin`.

---

## 4. Modelo de base de datos

Dump SQL crea la BD `backTarjetaVecino` con 6 tablas:

| Tabla | Campos clave | Notas |
|---|---|---|
| `persona` | `id_persona`, `rut` (único), `serial_number` (cifrado Fernet), nombres, apellidos, dirección, contacto | Estado activo/inactivo |
| `tarjeta` | `id_tarjeta`, `id_persona` (único), `numero_tarjeta` (único), `codigo_qr` (longtext base64), fechas, estado (activa/bloqueada/vencida) | FK → persona |
| `beneficios` | `id_beneficio`, nombre, `tipo_descuento` (porcentaje/monto_fijo/2x1), stock, fechas, comercio | 6 beneficios semilla |
| `historial_beneficios` | `id_historial`, `id_persona`, `id_beneficio`, `codigo_canje`, `fecha_uso` | FK → persona y beneficios |
| `usuario` | `id_usuario`, `username` (único), `password_hash`, `rol` (admin/funcionario), email | Admin y funcionario semilla |
| `auditoria` | `id_auditoria`, tabla afectada, acción, descripción, usuario, fecha | Log de operaciones |

**Nota:** la columna `codigo_canje` en `historial_beneficios` no tiene FK hacia una tabla de canjes (el modelo `canjes`/`canje_repository` existe en código, verificar si la tabla real falta en el SQL).

---

## 5. Problemas y archivos muertos detectados

1. **`.env` inexistente** — bloqueante para arrancar (README define las variables, pero no hay archivo).
2. **Dependencias no instaladas** — `fastapi` no importa en el entorno actual; no hay `venv/` creado.
3. **`app/core/config.py`** — (resuelto) ahora centraliza la configuración con `pydantic-settings`; `database.py`, `security.py`, `encryption.py`, `dec_services.py` y `main.py` leen desde `settings`.
4. **Archivos vacíos/muertos** — (resuelto) `app/dependencies/`, `app/routers/items.py`, `app/models/item.py` y los schemas por dominio fueron eliminados; los schemas viven en `app/models/schemas.py`.
5. **Nomenclatura inconsistente** — (resuelto) `Outh_*` renombrado a `usuario_*` (`usuario_router.py`, `usuario_service.py`, `usuario_repository.py`). Siguen existiendo dos routers con prefijo `/auth`: `auth_router` (login) y `usuario_router` (registro).
6. **Sin tests** — (resuelto) hay suite de pytest en `tests/` (BD de test `backTarjetaVecino_test`, ver AGENTS.md).
7. **Sin Docker** — (resuelto) hay `Dockerfile` y `docker-compose.yml` para BD MySQL + backend.
8. **SQLAlchemy listado en requirements pero no utilizado** — (obsoleto) el proyecto se migró a SQLAlchemy 2.0 (models en `app/models/orm.py`).
9. **`app/core/database.py`** — (resuelto) la sesión se inyecta con `get_db()` (DI): repos reciben `db` por parámetro y los servicios orquestan commit/rollback.

---

## 6. Checklist para poner el proyecto en marcha

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear .env (ver README) con DB_*, SECRET_KEY, FERNET_KEY, ALGORITHM,
#    ACCESS_TOKEN_EXPIRE_MINUTES, API_URL, API_TOKEN

# 4. Importar la base de datos en MySQL/MariaDB
mysql -u <usuario> -p < backTarjetaVecino.sql

# 5. Levantar el servicio
uvicorn main:app --reload
# -> http://127.0.0.1:8000/docs (Swagger)
```

Claves a generar (ver README):

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"          # SECRET_KEY
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # FERNET_KEY
```

---

## 7. Primer paso recomendado

**Levantar el servicio localmente.** Sin entorno ni BD corriendo no se puede probar nada ni avanzar en funcionalidad. Orden sugerido:

1. Crear `venv` e instalar dependencias.
2. Crear `.env` con los valores reales de la BD y claves generadas.
3. Importar `backTarjetaVecino.sql`.
4. Ejecutar `uvicorn main:app --reload` y validar `/docs` y `/health/test-db`.

Una vez corriendo, verificar los flujos completos: login admin → registro persona/tarjeta → generar QR → canje de beneficio → auditoría.

---

## 8. Mejoras sugeridas a futuro (no urgentes)

- (resuelto) Centralizar configuración en `app/core/config.py` con `pydantic-settings`.
- (resuelto) Eliminar archivos muertos (`items`, `dependencies/auth.py`, `config.py` vacío) y renombrar `Outh_*`.
- (resuelto) Agregar tests (pytest + httpx/TestClient) — suite en `tests/`.
- (resuelto) Manejo de errores y DI de sesión (`get_db()`) en la capa de repositorio.
- (resuelto) Endpoints de auditoría y canjes: revisar que apliquen protección por rol — verificado: `canjear`/`historial` son públicos por diseño (kiosco vecino) y la auditoría exige `require_admin`.
- (resuelto) Auditoría **completa y transaccional**: `registrar_auditoria` se ejecuta dentro del `commit()` del servicio (ya no es un commit separado post-router); se auditan personas, tarjetas, beneficios, canjes, registro de usuarios del sistema y regeneración de QR.
- (resuelto) Corregir `POST /qr/generar`: devolvía solo la longitud, era público y no persistía; ahora es admin, regenera y **persiste** el QR en `tarjeta.codigo_qr` y lo devuelve en base64.
