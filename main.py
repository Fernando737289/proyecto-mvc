import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.routers import (
    db_conection,
    users,
    qr_router,
    tarjeta_router,
    beneficio_router,
    verificacion_router,
    usuario_router,
    auth_router,
    auditoria_router,
    canjes_router
)
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=settings.LOG_LEVEL.upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger("main")

app = FastAPI(title="Mi API")

app.include_router(users.router)
app.include_router(db_conection.router)
app.include_router(qr_router.router)
app.include_router(tarjeta_router.router)
app.include_router(beneficio_router.router)
app.include_router(verificacion_router.router)
app.include_router(usuario_router.router)
app.include_router(auth_router.router)
app.include_router(canjes_router.router)
app.include_router(auditoria_router.router)

limiter = auth_router.limiter

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

@app.exception_handler(Exception)
async def manejar_error_no_controlado(request: Request, exc: Exception):
    logger.exception(
        "Error no controlado en %s %s",
        request.method,
        request.url.path,
        exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"msg": "Bienvenido a la API"}
