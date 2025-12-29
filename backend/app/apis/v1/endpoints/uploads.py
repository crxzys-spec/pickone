from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from app.apis.deps import require_scopes
from app.core.config import settings
from app.schemas.upload import UploadResponse

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".pdf"}


def _normalize_prefix(prefix: str) -> str:
    normalized = prefix.strip() or "/uploads"
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.rstrip("/")


def _build_file_url(relative_path: str, base_url: str | None) -> str:
    prefix = _normalize_prefix(settings.upload_url_prefix)
    normalized_path = relative_path.replace("\\", "/")
    url_path = f"{prefix}/{normalized_path}"
    base = settings.upload_base_url or base_url
    if base:
        return f"{base.rstrip('/')}{url_path}"
    return url_path


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
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename"
        )
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )

    base_dir = Path(settings.upload_dir).resolve()
    target_dir = base_dir / "experts"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{suffix}"
    target_path = target_dir / filename

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    relative_path = f"experts/{filename}"
    base_url = str(request.base_url).rstrip("/") if request else None
    return UploadResponse(
        url=_build_file_url(relative_path, base_url),
        path=relative_path,
        filename=filename,
    )
