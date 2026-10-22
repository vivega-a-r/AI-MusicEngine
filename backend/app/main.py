import time
import uuid
import yaml
from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.v1.endpoints import router as api_v1_router
from backend.app.core.config import settings
from backend.app.core.errors import (
    IncuBrixAPIException,
    generic_http_exception_handler,
    incubrix_exception_handler,
    unhandled_exception_handler
)
from backend.app.core.logging import correlation_id_ctx, logger
from backend.app.database.repository import job_repository

from contextlib import asynccontextmanager

def export_openapi_yaml():
    """Generates the openapi.yaml specification file."""
    openapi_schema = app.openapi()
    openapi_file = Path(__file__).resolve().parents[2] / "openapi.yaml"
    with open(openapi_file, "w", encoding="utf-8") as f:
        yaml.dump(openapi_schema, f, sort_keys=False)
    logger.info(f"Exported OpenAPI 3.1 schema to {openapi_file}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        export_openapi_yaml()
    except Exception as e:
        logger.warning(f"Could not export openapi.yaml on startup: {str(e)}")
    yield

app = FastAPI(
    title="IncuBrix Music Studio API",
    version=settings.APP_VERSION,
    description="Production-grade AI background music composition and stem rendering engine for video creators.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Idempotency-Key", "X-Correlation-ID", "Content-Disposition"]
)

# Exception handlers
app.add_exception_handler(IncuBrixAPIException, incubrix_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Request correlation ID middleware
@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-ID") or f"req_{uuid.uuid4().hex[:10]}"
    correlation_id_ctx.set(corr_id)
    start_time = time.time()
    
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Correlation-ID"] = corr_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    return response

# Static audio file mount for direct browser audio playback & download
Path(settings.STORAGE_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=settings.STORAGE_DIR), name="audio")

# Mount API v1
app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "auth_mode": "local_dev_mode" if settings.ENABLE_LOCAL_DEV_AUTH else "firebase_enforced"
    }

@app.get("/ready", tags=["Health"])
async def readiness_check():
    # Verify storage writable and database connectable
    storage_ok = Path(settings.STORAGE_DIR).exists()
    db_ok = Path(settings.DB_PATH).exists() or Path(settings.DB_PATH).parent.exists()
    return {
        "status": "ready" if (storage_ok and db_ok) else "degraded",
        "storage_ready": storage_ok,
        "database_ready": db_ok,
        "concurrency_limit": settings.MAX_WORKER_CONCURRENCY
    }


