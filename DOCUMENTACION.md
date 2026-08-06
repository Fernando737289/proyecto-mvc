# Documentación del proyecto — backend-TarjetaVecino

Documentación del estado **actual** del proyecto (post-migración a SQLAlchemy ORM). Explica qué hay, cómo está organizado y cómo funciona cada parte.

---

## 1. Resumen

Backend de la **Tarjeta Vecino**. Es una API REST que gestiona:

* Personas vecinas (con su número de serie de cédula cifrado).
* Tarjetas vecinas (con código QR y fecha de vencimiento).
* Beneficios y descuentos municipales.
* Canje de beneficios (con descuento de stock y registro de historial).
* Usuarios del sistema (`admin` / `funcionario`) con autenticación JWT.
* Auditoría de las operaciones administrativas.
* Validación de la vigencia de la cédula contra un servicio externo (DEC).

Se ejecuta con **Docker Compose** (MySQL 8.0 + API FastAPI) o directamente con `uvicorn`.

---

## 2. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.13 |
| Framework web | FastAPI 0.136 + Uvicorn |
| Validación | Pydantic 2.13 |
| Base de datos | MySQL 8.0 |
| ORM | SQLAlchemy 2.0.49 (acceso a BD) |
| Driver | `mysql-connector-python` (DBAPI de SQLAlchemy) |
| Autenticación | JWT (`python-jose`) + `passlib`/`bcrypt` |
| Cifrado sensible | `cryptography` (Fernet) |
| Rate limiting | `slowapi` (5 intentos/min en login) |
| QR | `qrcode` + `pillow` |
| HTTP externo | `httpx` |
| Contenedores | Docker + Docker Compose |

---

## 3. Estructura de directorios

```text
.
├── main.py                    # Punto de entrada: crea la app FastAPI y registra routers
├── requirements.txt           # Dependencias de Python
├── Dockerfile                 # Imagen del backend (python:3.13-slim + uvicorn)
├── docker-compose.yml         # Orquesta MySQL + backend
├── .dockerignore              # Excluye .env, venv, git, etc. del build
├── .gitignore                 # Excluye .env, venv, etc. de git
├── backTarjetaVecino.sql      # Esquema + datos semilla (se ejecuta al crear la BD)
├── README.md                  # Tutorial para levantar el servicio
├── ANALISIS.md                # Análisis técnico inicial del proyecto
└── app/
    ├── main/…                 # (no existe; la app es main.py en la raíz)
    ├── core/                  # Configuración y utilidades transversales
    │   ├── database.py        # Engine + SessionLocal + Base (SQLAlchemy)
    │   ├── security.py        # JWT + hash/verificación de contraseñas (passlib)
    │   ├── encryption.py      # Cifrado/descifrado Fernet (serial_number)
    │   ├── dependencies.py    # Dependencias: get_current_user, require_admin
    │   ├── generador_codigo.py# Código de canje aleatorio (20 caracteres)
    │   └── config.py          # VACÍO (archivo residual de plantilla)
    ├── models/                # Schemas Pydantic (entrada) y modelos ORM
    │   ├── orm.py             # Modelos ORM: Persona, Tarjeta, Beneficio, …
    │   ├── schemas.py         # Schemas de respuesta (from_attributes)
    │   ├── user.py            # User, UpdateEstadoPersonaRequest
    │   ├── tarjeta_model.py   # CreateTarjetaRequest, UpdateTarjetaRequest
    │   ├── beneficio_model.py # Beneficio
    │   ├── qr_model.py        # QRRequest
    │   ├── canjes.py          # CanjeSchema (no se usa en rutas actuales)
    │   ├── auth_model.py      # LoginRequest
    │   ├── Outh_Model.py      # CreateUsuarioRequest
    │   ├── verificacion.py    # VerificacionCedulaSchema
    │   └── item.py            # VACÍO (residual)
    ├── repository/            # Acceso a BD con SQLAlchemy (una capa por dominio)
    │   ├── user_repository.py
    │   ├── qr_repository.py
    │   ├── tarjeta_repository.py
    │   ├── beneficio_repository.py
    │   ├── canje_repository.py    # Transacción atómica de canje
    │   ├── historial_repository.py
    │   ├── auth_repository.py
    │   ├── outh_repository.py
    │   └── auditoria_repository.py
    ├── services/              # Lógica de negocio (orquestan repos)
    │   ├── user_service.py
    │   ├── qr_service.py
    │   ├── tarjeta_service.py
    │   ├── beneficio_service.py
    │   ├── canjes_service.py
    │   ├── historial_beneficio_service.py
    │   ├── auth_service.py
    │   ├── Outh_service.py
    │   ├── auditoria_service.py
    │   ├── db_service.py          # Health check de conexión
    │   └── dec_services.py        # Cliente HTTP del servicio externo DEC
    ├── routers/               # Endpoints HTTP
    │   ├── users.py
    │   ├── qr_router.py
    │   ├── tarjeta_router.py
    │   ├── beneficio_router.py
    │   ├── canjes_router.py
    │   ├── auth_router.py
    │   ├── Outh_router.py
    │   ├── auditoria_router.py
    │   ├── verificacion_router.py
    │   ├── db_conection.py
    │   └── items.py           # VACÍO (residual)
    └── dependencies/
        └── auth.py            # VACÍO (residual)
```

> **Archivos residuales**: `app/core/config.py`, `app/models/item.py`, `app/routers/items.py` y `app/dependencies/auth.py` están vacíos y **no se importan** en `main.py`. Pueden borrarse.

---

## 4. Arquitectura por capas

El proyecto sigue una arquitectura MVC por capas, donde cada petición fluye:

```text
RUTA (routers/)  →  SERVICIO (services/)  →  REPOSITORIO (repository/)  →  ORM (models/orm.py)  →  MySQL
```

* **Routers**: exponen los endpoints HTTP, reciben/validan el body con Pydantic, inyectan dependencias (auth) y devuelven respuestas con `response_model`.
* **Services**: contienen la lógica de negocio (validaciones, reglas, errores `HTTPException`).
* **Repositories**: encapsulan todas las consultas SQLAlchemy. **Cada función abre y cierra su propia sesión** (`SessionLocal`), y devuelve **objetos ORM**.
* **ORM**: modelos declarativos que mapean las tablas de MySQL.

Reglas de capas:

* Los repos no devuelven `HTTPException` salvo el flujo de canje (necesita hacer `rollback` dentro de su única transacción).
* Los schemas de respuesta (`app/models/schemas.py`) usan `ConfigDict(from_attributes=True)`, lo que permite serializar objetos ORM directamente y **omitir campos sensibles** (como `serial_number`).

---

## 5. Base de datos

### 5.1 Tablas (definidas en `backTarjetaVecino.sql`)

| Tabla | Descripción | Columnas principales |
|---|---|---|
| `persona` | Vecinos registrados | `id_persona` (PK), `rut` (unique), `serial_number` (cifrado), `nombres`, `apellidos`, `direccion`, `telefono`, `email`, `fecha_nacimiento`, `estado`, `fecha_creacion` |
| `tarjeta` | Tarjeta de cada vecino | `id_tarjeta` (PK), `id_persona` (FK unique), `numero_tarjeta` (unique), `codigo_qr`, `fecha_emision`, `fecha_vencimiento`, `estado` |
| `beneficios` | Catálogo de beneficios | `id_beneficio` (PK), `nombre`, `descripcion`, `tipo_descuento`, `valor_descuento`, `stock`, `fecha_inicio`, `fecha_vencimiento`, `comercio`, `estado` |
| `historial_beneficios` | Canjes realizados | `id_historial` (PK), `id_persona` (FK), `id_beneficio` (FK), `codigo_canje`, `fecha_uso` |
| `usuario` | Usuarios del sistema | `id_usuario` (PK), `username` (unique), `password_hash`, `rol`, `estado`, `fecha_creacion`, `email` |
| `auditoria` | Registro de acciones | `id_auditoria` (PK), `tabla_afectada`, `accion_realizada`, `descripcion`, `usuario_accion`, `fecha_accion` |

### 5.2 Modelos ORM (`app/models/orm.py`)

* `Persona` ↔ `Tarjeta`: relación uno a uno (`Tarjeta.persona`).
* `Persona` ↔ `HistorialBeneficio`: uno a muchos (`Persona.historiales`).
* `Beneficio` ↔ `HistorialBeneficio`: uno a muchos (`Beneficio.historiales`).
* `HistorialBeneficio.beneficio`: relación a `Beneficio` (se carga con `joinedload` en consultas de historial).

### 5.3 Datos semilla

El `backTarjetaVecino.sql` crea la BD y carga: 2 personas, 1 tarjeta, 6 beneficios, 3 canjes de historial y 2 usuarios (`admin`, `funcionario 1`). **Las contraseñas de estos usuarios no se conocen**; para probar endpoints protegidos hay que crear un usuario nuevo (ver `README.md`).

---

## 6. Autenticación y seguridad

* **JWT** (`app/core/security.py`): firma con `SECRET_KEY` + `ALGORITHM` (HS256), expiración `ACCESS_TOKEN_EXPIRE_MINUTES`. El token lleva `sub` (username), `id_usuario` y `rol`.
* **Contraseñas**: `passlib` con esquema `bcrypt` (hash y verificación). El registro de usuarios usa `hash_password()`.
* **Endpoints protegidos**: usan `HTTPBearer` + `require_admin` (`app/core/dependencies.py`), que valida el token y exige rol `admin`.
* **Cifrado de datos sensibles** (`app/core/encryption.py`): el `serial_number` de la cédula se guarda cifrado con **Fernet** (`FERNET_KEY`) y **nunca** se expone en las respuestas (`PersonaOut` lo omite).
* **Rate limiting**: `POST /auth/login` está limitado a **5 peticiones por minuto** por IP (`slowapi`).

---

## 7. Endpoints

### Health
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/health/test-db` | Público | Comprueba conexión a la BD |

### Users (personas)
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/users/` | Público | Lista personas (sin `serial_number`) |
| POST | `/users/usuarios` | Admin | Crea persona tras validar la cédula en el DEC |
| PUT | `/users/{id_persona}` | Admin | Actualiza persona |
| DELETE | `/users/{id_persona}` | Admin | Elimina persona |
| PATCH | `/users/{id_persona}/estado` | Admin | Cambia estado (activo/inactivo) |

### QR
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/qr/generar` | Público | Genera QR con datos de la persona y devuelve su longitud |

### Tarjeta
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/tarjeta/crear` | Admin | Crea tarjeta (valida coincidencia de nombres/apellidos/teléfono) |
| GET | `/tarjeta/buscar` | Público | Busca por `rut` o `numero_tarjeta` |
| PUT | `/tarjeta/{id_tarjeta}` | Admin | Actualiza estado y vencimiento |
| DELETE | `/tarjeta/{id_tarjeta}` | Admin | Elimina tarjeta |

### Beneficios
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/beneficios/crear` | Admin | Crea beneficio |
| GET | `/beneficios/` | Público | Lista beneficios activos |
| PUT | `/beneficios/actualizar/{id_beneficio}` | Admin | Actualiza nombre y descripción |
| DELETE | `/beneficios/eliminar/{id_beneficio}` | Admin | Eliminación **lógica** (`estado='inactivo'`) |

### Canjes
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/beneficios/canjear` | Público | Canjea un beneficio (`?id_persona=&id_beneficio=`) |
| GET | `/beneficios/historial/{id_persona}` | Público | Historial de canjes de una persona |

### Auth
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/auth/login` | Público (5/min) | Login, devuelve `access_token` |
| POST | `/auth/registro` | Admin | Crea usuario del sistema |

### Auditoría
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| GET | `/auditoria/` | Admin | Lista acciones registradas |

### Verificación de cédula (DEC)
| Método | Ruta | Acceso | Descripción |
|---|---|---|---|
| POST | `/verificaciones/validar-cedula` | Público | Valida vigencia de una cédula contra el servicio externo |

---

## 8. Flujo del canje (transacción atómica)

`POST /beneficios/canjear` ejecuta, en **una sola sesión** (`canje_repository.canjear_beneficio`):

1. Busca la persona por `id_persona` → si no existe: `404`.
2. Busca el beneficio por `id_beneficio` → si no existe: `404`.
3. Verifica `stock > 0` → si no: `400`.
4. Verifica que la persona no haya canjeado ya ese beneficio → si ya lo hizo: `400`.
5. Descuenta `stock -= 1` y registra un `historial_beneficios` con un código de canje único.
6. `commit()`. Ante cualquier error: `rollback()`.

Así, el descuento de stock y el registro del canje ocurren **juntos o no ocurren**.

---

## 9. Integración externa (DEC)

`app/services/dec_services.py` consume `POST URL_API` (p. ej. `https://5dev.dec.cl/api/v1/auth/validate_vigencia`) con:

* Header `X-API-KEY` con el token.
* Body `{"user_rut": ..., "serial_number": ...}`.
* Timeout de 10 s. Errores HTTP del servicio o de red se transforman en `HTTPException` claras.

La respuesta se interpreta en `user_service.create_user` (exige `Verificacion == "V"`) y en `verificacion_router`.

> **Nota sobre variables**: el código de `dec_services.py` lee `URL_API` y `DEC_API_KEY` desde el entorno. Con Docker, `docker-compose.yml` hace el mapeo desde `API_URL`/`API_TOKEN` del `.env`. En ejecución **local sin Docker**, el `.env` debe definir `URL_API` y `DEC_API_KEY` directamente.

---

## 10. Variables de entorno

| Variable | Uso | ¿Obligatoria? |
|---|---|---|
| `DB_HOST`, `DB_PORT` | Host/puerto de MySQL | Sí (solo local; en Docker las fija compose) |
| `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Credenciales de BD | Sí (compose tiene defaults `root`/`root123`/`backTarjetaVecino`) |
| `SECRET_KEY` | Firma de tokens JWT | Sí |
| `ALGORITHM` | Algoritmo JWT (`HS256`) | Sí (default) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Minutos de expiración del token | Sí (default 60) |
| `FERNET_KEY` | Clave de cifrado Fernet | Sí |
| `API_URL` / `API_TOKEN` | Endpoint y API key del DEC | Solo si se usa validación de cédula |

---

## 11. Docker

* **`Dockerfile`**: `python:3.13-slim`, instala `requirements.txt` y ejecuta `uvicorn main:app --host 0.0.0.0 --port 8000`.
* **`docker-compose.yml`**:
  * `db`: imagen `mysql:8.0`, puerto `3306`, volumen `db_data` (persistencia) y monta `backTarjetaVecino.sql` como init (la BD se crea sola en el primer arranque). Healthcheck con `mysqladmin ping`.
  * `backend`: build local, puerto `8000`, `depends_on` a la BD con `condition: service_healthy` (espera a que esté lista). Recibe las variables de entorno desde el `.env` del host.
  * `.env` se excluye del build (`.dockerignore`): la configuración viaja por Compose, no dentro de la imagen.

Ver el `README.md` para el tutorial completo de puesta en marcha.

---

## 12. Migración reciente a SQLAlchemy ORM

Cambios principales aplicados en esta versión:

* Se eliminó el uso directo de `mysql.connector`/`get_connection()`; ahora todo el acceso a datos usa **SQLAlchemy 2.0 ORM** (`SessionLocal`, modelos declarativos).
* Los repositorios devuelven **objetos ORM**; los routers serializan con `response_model` (`app/models/schemas.py`), lo que evita filtrar `serial_number`.
* El canje pasó a ser una **transacción atómica** dentro del repositorio.
* Se unificó el hashing de contraseñas con `passlib` (`outh_repository`).
* **Bugs corregidos**: eliminación/actualización de beneficios (SQL inválido), y recursión infinita en `tarjeta_service.get_tarjeta`/`update_tarjeta` (el nombre de la función del servicio opacaba al del repositorio).
