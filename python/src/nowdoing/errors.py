"""Exception hierarchy raised by :mod:`nowdoing`."""

from __future__ import annotations


class NowDoingError(Exception):
    """Base class for everything raised by the NowDoing SDK."""


class NowDoingHttpError(NowDoingError):
    """Raised when the Mac app returns a non-2xx response."""

    def __init__(self, status: int, server_message: str) -> None:
        super().__init__(f"NowDoing HTTP {status}: {server_message}")
        self.status = status
        self.server_message = server_message


class NowDoingAuthError(NowDoingHttpError):
    """401 — token, signature, timestamp or nonce was rejected."""


class NowDoingValidationError(NowDoingHttpError):
    """400 — the server rejected the request payload or query."""

    def __init__(self, server_message: str) -> None:
        super().__init__(400, server_message)


class NowDoingNotFoundError(NowDoingHttpError):
    """404 — referenced activity or endpoint does not exist."""

    def __init__(self, server_message: str) -> None:
        super().__init__(404, server_message)


class NowDoingReplayError(NowDoingHttpError):
    """409 — nonce already used inside the replay window."""

    def __init__(self, server_message: str) -> None:
        super().__init__(409, server_message)


class NowDoingUnavailableError(NowDoingHttpError):
    """503 — the corresponding handler is not currently wired up in the app."""

    def __init__(self, server_message: str) -> None:
        super().__init__(503, server_message)


def map_http_error(status: int, server_message: str) -> NowDoingHttpError:
    if status == 400:
        return NowDoingValidationError(server_message)
    if status == 401:
        return NowDoingAuthError(status, server_message)
    if status == 404:
        return NowDoingNotFoundError(server_message)
    if status == 409:
        return NowDoingReplayError(server_message)
    if status == 503:
        return NowDoingUnavailableError(server_message)
    return NowDoingHttpError(status, server_message)
