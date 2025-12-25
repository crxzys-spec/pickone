from __future__ import annotations

import secrets


def generate_code(prefix: str | None = None, length: int = 8) -> str:
    token = secrets.token_hex(max(1, length // 2))[:length]
    if prefix:
        return f"{prefix}_{token}"
    return token
