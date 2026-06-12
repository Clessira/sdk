"""Client SDK for the Clessira macOS app loopback HTTP API."""

from __future__ import annotations

from ._async_client import AsyncClessiraClient
from ._client import ClessiraClient
from .errors import (
    ClessiraAuthError,
    ClessiraError,
    ClessiraHttpError,
    ClessiraNotFoundError,
    ClessiraReplayError,
    ClessiraUnavailableError,
    ClessiraValidationError,
)
from .models import (
    ActivitySearchItem,
    CurrentActivity,
    LogEntryResult,
    StartActivityResult,
    Status,
    StatusActivity,
)

__all__ = [
    "ActivitySearchItem",
    "AsyncClessiraClient",
    "CurrentActivity",
    "LogEntryResult",
    "ClessiraAuthError",
    "ClessiraClient",
    "ClessiraError",
    "ClessiraHttpError",
    "ClessiraNotFoundError",
    "ClessiraReplayError",
    "ClessiraUnavailableError",
    "ClessiraValidationError",
    "StartActivityResult",
    "Status",
    "StatusActivity",
]
__version__ = "0.1.0"
