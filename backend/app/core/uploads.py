from __future__ import annotations

import base64
import hashlib
import hmac
import time
from urllib.parse import urlencode, urlparse

from app.core.config import settings


def _normalize_prefix(prefix: str) -> str:
    normalized = prefix.strip() or "/uploads"
    if not normalized.startswith("/"):
        normalized = f"/{normalized}"
    return normalized.rstrip("/")


def _normalize_relative_path(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("/")
    return normalized


def generate_upload_token(relative_path: str, ttl_seconds: int) -> str:
    exp = int(time.time()) + max(ttl_seconds, 1)
    payload = f"{relative_path}|{exp}".encode()
    secret = settings.secret_key.encode()
    signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
    token_raw = f"{exp}:{signature}".encode()
    return base64.urlsafe_b64encode(token_raw).decode().rstrip("=")


def verify_upload_token(token: str, relative_path: str) -> bool:
    if not token:
        return False
    padded = token + "=" * (-len(token) % 4)
    try:
        decoded = base64.urlsafe_b64decode(padded).decode()
    except (ValueError, UnicodeDecodeError):
        return False
    if ":" not in decoded:
        return False
    exp_str, signature = decoded.split(":", 1)
    try:
        exp = int(exp_str)
    except ValueError:
        return False
    if exp < int(time.time()):
        return False
    payload = f"{relative_path}|{exp}".encode()
    expected = hmac.new(settings.secret_key.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def build_upload_url(relative_path: str, base_url: str | None = None) -> str:
    prefix = _normalize_prefix(settings.upload_url_prefix)
    normalized = _normalize_relative_path(relative_path)
    url_path = f"{prefix}/{normalized}"
    base = settings.upload_base_url or base_url
    if base:
        return f"{base.rstrip('/')}{url_path}"
    return url_path


def build_signed_upload_url(
    relative_path: str, base_url: str | None = None, ttl_minutes: int | None = None
) -> str:
    ttl = ttl_minutes if ttl_minutes is not None else settings.upload_token_ttl_minutes
    token = generate_upload_token(_normalize_relative_path(relative_path), ttl * 60)
    url = build_upload_url(relative_path, base_url)
    joiner = "&" if "?" in url else "?"
    return f"{url}{joiner}{urlencode({'token': token})}"


def extract_relative_path(url_or_path: str) -> str | None:
    value = (url_or_path or "").strip()
    if not value:
        return None
    if "://" in value:
        parsed = urlparse(value)
        value = parsed.path
    else:
        value = value.split("?", 1)[0].split("#", 1)[0]
    prefix = _normalize_prefix(settings.upload_url_prefix)
    if value.startswith(prefix + "/"):
        return _normalize_relative_path(value[len(prefix) + 1 :])
    if value.startswith("experts/"):
        return _normalize_relative_path(value)
    return None
