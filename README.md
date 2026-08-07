# backend-TarjetaVecino

Backend de la Tarjeta Vecino. API REST construida con **FastAPI** y **MySQL**, con capa de datos sobre **SQLAlchemy ORM**.

## Contenido

1. [Requisitos previos](#requisitos-previos)
2. [Paso 1 - Crear el archivo `.env`](#paso-1---crear-el-archivo-env)
3. [Paso 2 - Levantar el servicio con Docker (recomendado)](#paso-2---levantar-el-servicio-con-docker-recomendado)
4. [Paso 3 - Verificar que todo funciona](#paso-3---verificar-que-todo-funciona)
5. [Paso 4 - Uso y endpoints de ejemplo](#paso-4---uso-y-endpoints-de-ejemplo)
6. [Comandos útiles](#comandos-utiles)
7. [Solución de problemas](#solucion-de-problemas)
8. [Ejecución local (sin Docker)](#ejecucion-local-sin-docker)

---

## Requisitos previos

* **Docker** con **Docker Compose** instalados.
* Puertos libres:
  * `3306` — MySQL.
  * `8000` — API.
* (Opcional) **Python 3.13** si quieres ejecutar sin Docker.

Para verificar que Docker está disponible:

```bash
docker --version
docker compose version
```

---

## Paso 1 - Crear el archivo `.env`

Crea un archivo `.env` en la raíz del proyecto. Es el que usará Docker Compose para inyectar la configuración al contenedor del backend.

```env
# base de datos
DB_USER=root
DB_PASSWORD=root123
DB_NAME=backTarjetaVecino

# jwt
SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# fernet (cifrado de datos sensibles)
FERNET_KEY=

# api externa de validacion de cedula
API_URL=https://5dev.dec.cl/api/v1/auth/validate_vigencia
API_TOKEN=
```

### Generar `SECRET_KEY` (firma de tokens JWT)

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

### Generar `FERNET_KEY` (cifrado del número de serie de la cédula)

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copia los valores generados y asígnalos en el `.env`.

### Importante

* **No subas el archivo `.env` al repositorio** (está excluido por `.gitignore` y `.dockerignore`).
* Cada instalación debe generar sus propias claves.
* `SECRET_KEY` y `FERNET_KEY` son obligatorias: sin ellas `docker compose up` no arranca.
* `API_URL` y `API_TOKEN` solo son necesarias si se usará el flujo de alta de personas (`POST /users/usuarios`), que valida la cédula contra el servicio externo del DEC.

> Nota: en modo Docker, `DB_HOST` y `DB_PORT` los fija el propio `docker-compose.yml` (`db` / `3306`). Las variables `DB_*` del `.env` solo se usan para la ejecución local.

---

## Paso 2 - Levantar el servicio con Docker (recomendado)

Desde la raíz del proyecto:

```bash
docker compose up -d --build
```

Qué hace este comando:

1. Construye la imagen del backend (instala `requirements.txt` con `pip`).
2. Arranca **MySQL 8.0** en el contenedor `tarjetavecino_db`.
3. En el **primer arranque** crea la base de datos, las tablas y los datos de ejemplo automáticamente a partir de `backTarjetaVecino.sql` (no hay que importar nada a mano).
4. Espera a que la base de datos esté sana (healthcheck) y recién entonces levanta el backend en `tarjetavecino_backend`.

Para ver el estado de los contenedores:

```bash
docker compose ps
```

Salida esperada: ambos servicios `running` y el contenedor de BD `healthy`.

---

## Paso 3 - Verificar que todo funciona

1. **Logs del backend** (debe aparecer `Application startup complete`):

   ```bash
   docker compose logs backend
   ```

2. **Endpoint raíz:**

   ```bash
   curl http://localhost:8000/
   ```

   Respuesta esperada:

   ```json
   {"msg":"Bienvenido a la API"}
   ```

3. **Prueba de conexión a la base de datos:**

   ```bash
   curl http://localhost:8000/health/test-db
   ```

   Respuesta esperada:

   ```json
   {"conexion":"exitosa","baseDeDatos":"backTarjetaVecino"}
   ```

4. **Documentación Swagger (interactiva):**

   ```
   http://localhost:8000/docs
   ```

---

## Paso 4 - Uso y endpoints de ejemplo

### Autenticación

La mayoría de los endpoints requieren un token JWT con rol `admin` (`Authorization: Bearer <token>`).

Los usuarios de ejemplo se crean con la base de datos semilla (`admin`, `funcionario 1`), pero **sus contraseñas no se conocen**. Para poder probar los endpoints protegidos, crea un usuario administrador desde el contenedor:

```bash
docker compose exec backend python -c "
from app.core.database import SessionLocal
from app.repository.usuario_repository import crear_usuario

with SessionLocal() as db:
    crear_usuario(db, 'miadmin', 'miadmin@example.com', 'ClaveSegura123!')
    db.commit()
"
```

Luego asígnale rol de administrador:

```bash
docker compose exec db mysql -uroot -proot123 backTarjetaVecino -e \
"UPDATE usuario SET rol='admin' WHERE username='miadmin';"
```

Y obtén el token:

```bash
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"miadmin@example.com","password":"ClaveSegura123!"}'
```

### Ejemplos de endpoints

```bash
# Listar beneficios activos (público)
curl http://localhost:8000/beneficios/

# Listar personas registradas (público)
curl http://localhost:8000/users/

# Buscar tarjeta por RUT (público)
curl "http://localhost:8000/tarjeta/buscar?rut=21817151-6"

# Historial de canjes de una persona (público)
curl http://localhost:8000/beneficios/historial/13

# Canjear un beneficio (id_persona, id_beneficio)
curl -X POST "http://localhost:8000/beneficios/canjear?id_persona=13&id_beneficio=6"

# Con token de administrador
curl http://localhost:8000/beneficios/ -H "Authorization: Bearer $TOKEN"

# Regenerar el QR de una tarjeta y obtenerlo en base64 (solo admin)
curl -X POST http://localhost:8000/qr/generar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"rut":"21817151-6"}'
```

---

## Comandos útiles

| Comando | Efecto |
|---|---|
| `docker compose up -d --build` | Construye y levanta el stack. |
| `docker compose ps` | Estado de los contenedores. |
| `docker compose logs -f backend` | Logs del backend en tiempo real. |
| `docker compose up -d --build backend` | Reconstruye solo el backend tras cambios de código. |
| `docker compose down` | Detiene los contenedores (conserva los datos en el volumen). |
| `docker compose down -v` | Detiene y **borra el volumen** de la base de datos (vuelve al estado semilla en el próximo arranque). |
| `docker compose restart` | Reinicia los contenedores. |
| `docker compose exec backend python -m pytest` | Ejecuta la suite de tests (usa una BD de test separada `backTarjetaVecino_test`; no toca tus datos). |

---

## Solucion de problemas

| Problema | Solución |
|---|---|
| `docker compose up` falla y pide `SECRET_KEY` o `FERNET_KEY` | Completa esas variables en el `.env` (ver [Paso 1](#paso-1---crear-el-archivo-env)). |
| El backend entra en bucle de reinicios (`Restarting`) | `docker compose logs backend`. Causas típicas: la base de datos aún no estaba lista o falta configuración en `.env`. |
| El puerto `3306` o `8000` está ocupado | Cambia el mapeo de puertos en `docker-compose.yml` (ej. `"3307:3306"`) o detén el otro servicio. |
| Quiero resetear los datos de la base de datos | `docker compose down -v && docker compose up -d --build`. |
| El build falla al resolver `pypi.org` | Revisa DNS, proxy o configuración de red del equipo (es un problema del host, no del proyecto). |
| `GET /users/` o `/beneficios/` responde `500` | Verifica que la base de datos esté `healthy` y que el `.env` apunte a la BD correcta. |

---

## Ejecucion local (sin Docker)

Pasos si prefieres correr el backend directamente con Python:

1. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Crear la base de datos importando el SQL (requiere un MySQL local):

   ```bash
   mysql -u root -p < backTarjetaVecino.sql
   ```

3. En el `.env`, apunta al MySQL local:

   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```

4. Arrancar el servidor:

   ```bash
   uvicorn main:app --reload
   ```

   Disponible en `http://127.0.0.1:8000` y Swagger en `http://127.0.0.1:8000/docs`.
