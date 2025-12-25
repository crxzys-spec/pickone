import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.apis.v1.api import api_router

app = FastAPI(title="PickOne API")

app.include_router(api_router, prefix="/api/v1")

logger = logging.getLogger(__name__)


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
