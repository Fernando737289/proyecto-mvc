# AGENTS.md

Backend FastAPI + MySQL de la "Tarjeta Vecino". Arquitectura en capas: `app/routers/` → `app/services/` → `app/repository/`. Más detalle en `README.md`, `DOCUMENTACION.md`, `ANALISIS.md` (en español).

## Ejecución y verificación

- Todo corre con Docker: `docker compose up -d --build`. Local: `uvicorn main:app --reload` (requiere MySQL local y `.env` con `DB_HOST`/`DB_PORT`).
- `.env` es obligatorio y está gitignoreado; `SECRET_KEY` y `FERNET_KEY` son obligatorias o el backend no arranca. Existe `.env.example` como plantilla.
- La configuración se centraliza en `app/core/config.py` (pydantic-settings): `settings` se importa en `database.py`, `security.py`, `encryption.py`, `dec_services.py` y `main.py`. **No uses `os.getenv` + `load_dotenv` directo en módulos nuevos.**
- **Tests (pytest)**: correr con `docker compose exec backend python -m pytest` (pytest está en `requirements.txt`). Los tests viven en `tests/` y usan una BD de test separada `backTarjetaVecino_test` (se crea sola vía `CREATE DATABASE` + `alembic upgrade head` en `tests/conftest.py`; `os.environ["DB_NAME"]` se setea ANTES de importar `app`, así que `settings`/`engine` apuntan a la BD de test). Cada test arranca con las tablas truncadas (aislamiento total). El rate limit de login se desactiva con `limiter.enabled = False`. El DEC externo se mockea vía `monkeypatch` de `app.services.user_service.validar_vigencia_rut` (`dec_valida`/`dec_no_vigente`). No hay CI ni linter.

## Esquema de BD

- **Alembic integrado** (`alembic/` + `alembic.ini`): `env.py` usa `settings` y `Base`; la baseline `0001_esquema_inicial.py` es **idempotente** (omite tablas ya existentes), así que `alembic upgrade head` funciona tanto en BD recién creada como en la generada por el dump. El backend lo ejecuta en su arranque (CMD del Dockerfile) antes de levantar uvicorn.
- El esquema vive en: `backTarjetaVecino.sql` (DDL + datos semilla, auto-importado en el primer arranque del contenedor `db`), los modelos SQLAlchemy en `app/models/orm.py` (estilo 2.0 `Mapped[]`/`mapped_column()`, MySQL: `LONGTEXT` para `codigo_qr`, ENUMs y uniques con nombre) y la baseline de Alembic. **Verifica que modelos y BD no diverjan con `docker exec tarjetavecino_backend alembic check`** (las dependencias viven en el contenedor).
- Para un cambio de esquema: modifica `orm.py`, crea la migración (`alembic revision --autogenerate -m "..."` comparando contra la BD, luego revísala y ajusta el nombre de constraints/índices) y refleja el cambio en `backTarjetaVecino.sql`.
- Para regenerar la BD: `docker compose down -v && docker compose up -d --build` (borra el volumen `db_data`; el dump se reimporta y Alembic sella la baseline).
- La DB se monta como MySQL 8.0; el driver real es `mysql-connector-python` (ver `app/core/database.py`).

## Gotchas no obvios

- **Contraseñas de los usuarios semilla (`admin`, `funcionario 1`) no se conocen.** Para probar endpoints protegidos hay que crear un admin: `crear_usuario(...)` desde `app/repository/usuario_repository.py` y luego `UPDATE usuario SET rol='admin' ...` (pasos en README "Paso 4").
- **Variables DEC**: `app/services/dec_services.py` lee `API_URL`/`API_TOKEN` desde `settings` (`.env`). Docker Compose las mapea (`API_URL: ${API_URL}`, `API_TOKEN: ${API_TOKEN}`). Si están vacías, el flujo de validación de cédula devuelve 503 (servicio externo no disponible).
- Autenticación: JWT Bearer con claim `rol` en el token; `app/core/dependencies.py` (`require_admin`) exige `rol == "admin"`. Endpoints sin `require_admin` son públicos.
- Rate limit (slowapi): `/auth/login` está limitado a 5/min por IP.
- CORS abierto a todo (`allow_origins=["*"]`) en `main.py`.

## Código muerto / trampas de nombres

- Los schemas de entrada/salida están **consolidados** en `app/models/schemas.py` (incluida la validación de RUT chileno). No crees archivos de modelo nuevos por dominio.
- `app/routers/items.py`, `app/models/item.py`, `app/models/canjes.py` y `app/dependencies/` fueron **eliminados** (no se usaban).
- El módulo `usuario_*` (renombrado desde `Outh_*`) es el dominio de **gestión de usuarios/admin**: `app/routers/usuario_router.py` expone `POST /auth/registro`. No confundir con `auth_router.py` (login).
- Los repositorios reciben la sesión por **inyección** (`db: Session` como primer parámetro, inyectada en los routers con `Depends(get_db)` de `app/core/database.py`). **No crean ni cierran sesiones, no hacen `commit` ni `rollback`**: los servicios son dueños de la transacción (`db.commit()` al éxito, `db.rollback()` en errores). Los repos de creación hacen `db.flush()` para poblar el PK.
- **Auditoría transaccional**: toda operación de escritura (personas, tarjetas, beneficios, canjes, registro de usuarios y regeneración de QR) deja una fila en `auditoria`. `registrar_auditoria` se llama **dentro del servicio, antes de su `db.commit()`** (un solo commit para operación + auditoría); no hace `commit` propio. Los routers NO registran auditoría: solo pasan `admin["sub"]` como `usuario_accion` (el kiosco usa `"publico"`). Si agregas una mutación nueva, sigue este patrón.
- Los routers serializan con `response_model` (en `app/models/schemas.py`) y los repos devuelven objetos ORM; esto oculta `serial_number` (cifrado con Fernet). No devuelvas ORM directo sin pasar por `response_model`.
- **Manejo de errores**: los `except Exception` de los servicios NUNCA exponen `str(e)` en el `detail` (respuestas 500 genéricas en español) y deben loguear la causa con `logger.exception(...)` (`logger = logging.getLogger(__name__)` por módulo; `logging.basicConfig` en `main.py`, nivel en `settings.LOG_LEVEL`). Existe un handler global en `main.py` (`@app.exception_handler(Exception)`) que devuelve 500 JSON y registra el traceback; no repitas ese handler en servicios. `HTTPException` (400/401/403/404/409/422...) se usa para errores esperados y no se loguea.
- `dec_services` no filtra el texto del servicio externo al cliente: errores HTTP del DEC → `502`, problemas de red/URL vacía → `503` (cubre `httpx.HTTPError`, incluido `InvalidURL`).
- El rate limit de slowapi usa **un solo `Limiter`** (definido en `app/routers/auth_router.py`, reutilizado en `main.py`). No crees instancias nuevas de `Limiter`.

## Entorno

- Python 3.13 (imagen `python:3.13-slim`). Dependencias fijadas en `requirements.txt`.
