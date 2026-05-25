"""Client SDK for the NowDoing macOS app loopback HTTP API."""

from __future__ import annotations

from ._async_client import AsyncNowDoingClient
from ._client import NowDoingClient
from .errors import (
    NowDoingAuthError,
    NowDoingError,
    NowDoingHttpError,
    NowDoingNotFoundError,
    NowDoingReplayError,
    NowDoingUnavailableError,
    NowDoingValidationError,
)
from .models import ActivitySearchItem, CurrentActivity, StartActivityResult

__all__ = [
    "ActivitySearchItem",
    "AsyncNowDoingClient",
    "CurrentActivity",
    "NowDoingAuthError",
    "NowDoingClient",
    "NowDoingError",
    "NowDoingHttpError",
    "NowDoingNotFoundError",
    "NowDoingReplayError",
    "NowDoingUnavailableError",
    "NowDoingValidationError",
    "StartActivityResult",
]
__version__ = "0.1.0"
