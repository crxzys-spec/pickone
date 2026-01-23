from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.apis.deps import require_scopes
from app.core.config import settings
from app.core.ratelimit import enforce_rate_limit
from app.core.uploads import build_signed_upload_url
from app.schemas.upload import UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}


def _copy_with_limit(file: UploadFile, target_path: Path, max_bytes: int) -> None:
    written = 0
    with target_path.open("wb") as buffer:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if max_bytes and written > max_bytes:
                buffer.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File too large",
                )
            buffer.write(chunk)


def _save_expert_credential(request: Request, file: UploadFile) -> UploadResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename"
        )
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )
    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )

    base_dir = Path(settings.upload_dir).resolve()
    target_dir = base_dir / "experts"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target_path = target_dir / filename

    max_bytes = max(settings.upload_max_mb, 0) * 1024 * 1024
    _copy_with_limit(file, target_path, max_bytes)

    relative_path = f"experts/{filename}"
    base_url = str(request.base_url).rstrip("/") if request else None
    return UploadResponse(
        url=build_signed_upload_url(relative_path, base_url),
        path=relative_path,
        filename=filename,
    )


@router.post(
    "/expert-credential",
    dependencies=[Depends(require_scopes(["expert:write"]))],
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_expert_credential(
    request: Request,
    file: UploadFile = File(...),
):
    return _save_expert_credential(request, file)


@router.post(
    "/expert-credential-public",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_expert_credential_public(
    request: Request,
    file: UploadFile = File(...),
):
    enforce_rate_limit(
        request,
        "public-upload",
        settings.rate_limit_public_upload_per_hour,
        3600,
    )
    return _save_expert_credential(request, file)
