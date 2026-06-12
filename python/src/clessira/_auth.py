"""HMAC request signing — must stay bit-for-bit identical to ``BranchChangeServer.requestSignature`` on the Swift side."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time


def make_nonce() -> str:
    """Return 32 lowercase-hex chars (16 random bytes). Within the server's 16..128 alnum window."""
    return secrets.token_hex(16)


def timestamp_seconds(now: float | None = None) -> str:
    return str(int(time.time() if now is None else now))


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sign_request(
    *,
    token: str,
    method: str,
    target: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    """Compute the X-Clessira-Signature header value.

    Canonical string: ``METHOD\\ntarget\\ntimestamp\\nnonce\\nsha256_hex(body)``.
    """
    body_hash = sha256_hex(body)
    canonical = "\n".join([method.upper(), target, timestamp, nonce, body_hash])
    return hmac.new(token.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()
