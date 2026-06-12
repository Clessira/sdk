"""Exception hierarchy raised by :mod:`clessira`."""

from __future__ import annotations


class ClessiraError(Exception):
    """Base class for everything raised by the Clessira SDK."""


class ClessiraHttpError(ClessiraError):
    """Raised when the Mac app returns a non-2xx response."""

    def __init__(self, status: int, server_message: str) -> None:
        super().__init__(f"Clessira HTTP {status}: {server_message}")
        self.status = status
        self.server_message = server_message


class ClessiraAuthError(ClessiraHttpError):
    """401 — token, signature, timestamp or nonce was rejected."""


class ClessiraValidationError(ClessiraHttpError):
    """400 — the server rejected the request payload or query."""

    def __init__(self, server_message: str) -> None:
        super().__init__(400, server_message)


class ClessiraNotFoundError(ClessiraHttpError):
    """404 — referenced activity or endpoint does not exist."""

    def __init__(self, server_message: str) -> None:
        super().__init__(404, server_message)


class ClessiraReplayError(ClessiraHttpError):
    """409 — nonce already used inside the replay window."""

    def __init__(self, server_message: str) -> None:
        super().__init__(409, server_message)


class ClessiraUnavailableError(ClessiraHttpError):
    """503 — the corresponding handler is not currently wired up in the app."""

    def __init__(self, server_message: str) -> None:
        super().__init__(503, server_message)


def map_http_error(status: int, server_message: str) -> ClessiraHttpError:
    if status == 400:
        return ClessiraValidationError(server_message)
    if status == 401:
        return ClessiraAuthError(status, server_message)
    if status == 404:
        return ClessiraNotFoundError(server_message)
    if status == 409:
        return ClessiraReplayError(server_message)
    if status == 503:
        return ClessiraUnavailableError(server_message)
    return ClessiraHttpError(status, server_message)
