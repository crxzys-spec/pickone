import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.apis.v1.api import api_router
from app.core.config import settings

app = FastAPI(title="PickOne API")

app.include_router(api_router, prefix="/api/v1")

logger = logging.getLogger(__name__)
DIST_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
INDEX_PATH = DIST_DIR / "index.html"
UPLOAD_DIR = Path(settings.upload_dir).resolve()
UPLOAD_URL_PREFIX = settings.upload_url_prefix or "/uploads"
if not UPLOAD_URL_PREFIX.startswith("/"):
    UPLOAD_URL_PREFIX = f"/{UPLOAD_URL_PREFIX}"
UPLOAD_URL_PREFIX = UPLOAD_URL_PREFIX.rstrip("/")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error")
    detail = str(exc) or exc.__class__.__name__
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail},
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse | FileResponse:
    request_path = request.url.path
    if (
        exc.status_code == 404
        and INDEX_PATH.exists()
        and not request_path.startswith("/api")
        and not request_path.startswith("/assets")
        and not Path(request_path).suffix
    ):
        return FileResponse(INDEX_PATH)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def _mount_frontend(app: FastAPI) -> None:
    if DIST_DIR.exists():
        app.mount("/", StaticFiles(directory=str(DIST_DIR), html=True), name="static")
    else:
        logger.info("Frontend dist not found at %s", DIST_DIR)


def _mount_uploads(app: FastAPI) -> None:
    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        logger.exception("Failed to create upload dir at %s", UPLOAD_DIR)
        return
    app.mount(
        UPLOAD_URL_PREFIX, StaticFiles(directory=str(UPLOAD_DIR)), name="uploads"
    )


_mount_uploads(app)
_mount_frontend(app)
