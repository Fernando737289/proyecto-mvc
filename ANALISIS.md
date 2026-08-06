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
| `core/` | `database.py`, `security.py`, `encryption.py`, `generador_codigo.py`, `dependencies.py` | Conexión MySQL, hash/JWT, cifrado Fernet, generación de códigos, dependencias de auth (JWT + admin) |
| `dependencies/` | `auth.py` | **VACÍO** — archivo muerto |
| `models/` | `user`, `tarjeta_model`, `qr_model`, `beneficio_model`, `canjes`, `verificacion`, `auth_model`, `Outh_Model`, `item` | Schemas Pydantic de entrada/salida |
| `repository/` | `user`, `tarjeta`, `qr`, `beneficio`, `canje`, `historial`, `auditoria`, `auth`, `outh` | Consultas SQL directas |
| `services/` | `user_service`, `tarjeta_service`, `qr_service`, `beneficio_service`, `canjes_service`, `historial_beneficio_service`, `auditoria_service`, `auth_service`, `Outh_service`, `db_service`, `dec_services` | Lógica de negocio y orquestación |
| `routers/` | 12 routers (21 endpoints) | Capa HTTP |

---

## 3. Endpoints por router

| Router | Prefijo | Métodos | Protección |
|---|---|---|---|
| `db_conection` | `/health` | GET `/test-db` | Pública |
| `auth_router` | `/auth` | POST `/login` (límite 5/min) | Pública |
| `Outh_router` | `/auth` | POST `/registro` | Admin |
| `users` | `/users` | GET `/`, POST `/usuarios`, PUT `/{id}`, DELETE `/{id}`, PATCH `/{id}/estado` | CRUD admin (GET pública) |
| `qr_router` | (a definir) | POST `/generar` | — |
| `tarjeta_router` | `/tarjeta` | POST `/crear`, GET `/buscar`, PUT `/{id}`, DELETE `/{id}` | Admin (GET pública) |
| `beneficio_router` | `/beneficios` | POST `/crear`, GET `/`, PUT `/actualizar/{id}`, DELETE `/eliminar/{id}` | — |
| `canjes_router` | — | POST `/canjear`, GET `/historial/{id_persona}` | — |
| `verificacion_router` | `/verificaciones` | POST `/validar-cedula` | Pública (llama a DEC) |
| `auditoria_router` | — | GET `/` | — |

**Observación:** los prefijos y la protección de `qr_router`, `beneficio_router`, `canjes_router` y `auditoria_router` no se revisaron en detalle; falta confirmar si aplican `require_admin`.

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
3. **`app/core/config.py`** — vacío. La configuración está dispersa en `os.getenv`/`load_dotenv` dentro de cada módulo en lugar de centralizarse (aunque `pydantic-settings` ya está en requirements).
4. **Archivos vacíos/muertos:** `app/dependencies/auth.py`, `app/routers/items.py`, `app/models/item.py`.
5. **Nomenclatura inconsistente:** `Outh_router.py` / `Outh_service.py` (probablemente deberían ser "Auth"). Además hay dos routers con prefijo `/auth` (`auth_router` y `Outh_router`).
6. **Sin tests:** no existe ningún `test_*.py`.
7. **Sin Docker:** no hay `Dockerfile` ni `docker-compose` para replicar el entorno.
8. **SQLAlchemy listado en requirements** pero no utilizado (se usa SQL directo con mysql-connector).
9. **`app/core/database.py`**: la conexión no maneja errores ni cierra conexiones; riesgo de dejar sockets abiertos.

---

## 6. Checklist para poner el proyecto en marcha

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear .env (ver README) con DB_*, SECRET_KEY, FERNET_KEY, ALGORITHM,
#    ACCESS_TOKEN_EXPIRE_MINUTES, DEC_API_KEY, URL_API

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

- Centralizar configuración en `app/core/config.py` con `pydantic-settings`.
- Eliminar archivos muertos (`items`, `dependencies/auth.py`, `config.py` vacío).
- Renombrar `Outh_*` → `Auth_*` para consistencia.
- Agregar tests (pytest + httpx/TestClient) y Docker (Dockerfile + compose para BD + app).
- Manejo de errores y cierre de conexiones en `database.py` (idealmente un pool o un repo por request).
- Endpoints de auditoría y canjes: revisar que apliquen protección por rol.
