import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine
from app.routers import productos
from app.schemas import Salud

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("inventario")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # crea las tablas si no existen
    log.info("API lista (%s)", settings.environment)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "API REST de inventario: productos, búsqueda, paginación, "
        "movimientos de stock y resumen. Hecha con FastAPI + PostgreSQL."
    ),
    lifespan=lifespan,
    contact={"name": "Dante Mendoza"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def tiempo_de_respuesta(request: Request, call_next):
    inicio = time.perf_counter()
    respuesta = await call_next(request)
    ms = (time.perf_counter() - inicio) * 1000
    respuesta.headers["X-Response-Time-ms"] = f"{ms:.1f}"
    log.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, respuesta.status_code, ms)
    return respuesta


@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse("/docs")


@app.get("/health", response_model=Salud, tags=["Sistema"], summary="Estado de la API y la base")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return Salud(
        status="ok" if db_ok else "degradado",
        version=settings.app_version,
        entorno=settings.environment,
        base_de_datos="conectada" if db_ok else "sin conexion",
    )


app.include_router(productos.router)
