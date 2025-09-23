import os
import logging
from typing import List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from backend import router as backend_router
from frontend import router as frontend_router

# ========= Config por ambiente =========
APP_TITLE = "PDF Editável — Modular"
DISABLE_DOCS = os.getenv("DISABLE_DOCS", "0") == "1"

ALLOWED_ORIGINS: List[str] = (
    [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
    if os.getenv("ALLOWED_ORIGINS")
    else ["*"]
)

TRUSTED_HOSTS_ENV: Optional[str] = os.getenv("TRUSTED_HOSTS")
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))

# ========= App =========
app = FastAPI(
    title=APP_TITLE,
    docs_url=None if DISABLE_DOCS else "/docs",
    redoc_url=None if DISABLE_DOCS else "/redoc",
    openapi_url=None if DISABLE_DOCS else "/openapi.json",
)

logger = logging.getLogger("uvicorn.error")

# ========= Middlewares =========
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if TRUSTED_HOSTS_ENV:
    hosts = [h.strip() for h in TRUSTED_HOSTS_ENV.split(",") if h.strip()]
    if hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=hosts)

@app.middleware("http")
async def limit_content_length(request: Request, call_next):
    cl = request.headers.get("content-length")
    try:
        if cl is not None and int(cl) > MAX_UPLOAD_MB * 1024 * 1024:
            return JSONResponse(
                {"detail": f"Tamanho máximo permitido: {MAX_UPLOAD_MB} MB"},
                status_code=413,
            )
    except ValueError:
        pass
    return await call_next(request)

# ========= Static /assets (raiz ou backend/assets) =========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
BACKEND_ASSETS_DIR = os.path.join(BASE_DIR, "backend", "assets")

if os.path.isdir(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
    logger.info("Servindo /assets de %s", ASSETS_DIR)
elif os.path.isdir(BACKEND_ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=BACKEND_ASSETS_DIR), name="assets")
    logger.info("Servindo /assets de %s", BACKEND_ASSETS_DIR)
else:
    logger.warning(
        "Pasta 'assets' não encontrada (nem em ./assets nem em ./backend/assets) — /assets não será servido."
    )

# ========= Routers =========
app.include_router(frontend_router)           # rotas de páginas
app.include_router(backend_router, prefix="") # API (/api/...)

# ========= Healthcheck =========
@app.get("/healthz", tags=["infra"])
def healthz():
    return {"status": "ok"}

# ========= Handler global =========
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Erro não tratado em %s %s", request.method, request.url)
    return JSONResponse({"detail": "Erro interno"}, status_code=500)
