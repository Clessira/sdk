"""Loopback fake server that mirrors BranchChangeServer's auth + replay checks."""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable, Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import urlparse

import pytest

from clessira._auth import sign_request

Handler = Callable[["FakeRequest"], "FakeResponse"]


class FakeRequest:
    def __init__(self, method: str, path: str, query: str, body: bytes,
                 headers: dict[str, str]) -> None:
        self.method = method
        self.path = path
        self.query = query
        self.body = body
        self.headers = headers


class FakeResponse:
    def __init__(self, status: int = 200, body: Any | None = None) -> None:
        self.status = status
        self.body = body if body is not None else {"ok": True}


class FakeServer:
    def __init__(self, token: str, handler: Handler) -> None:
        self.token = token
        self.handler = handler
        self.requests: list[FakeRequest] = []
        self.seen_nonces: set[str] = set()
        self._httpd = HTTPServer(("127.0.0.1", 0), self._build_request_handler())
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=2)

    def _build_request_handler(self) -> type[BaseHTTPRequestHandler]:
        outer = self

        class _Handler(BaseHTTPRequestHandler):
            def log_message(self, *_: Any, **__: Any) -> None:  # silence
                pass

            def _read_body(self) -> bytes:
                length = int(self.headers.get("content-length", "0"))
                return self.rfile.read(length) if length else b""

            def _serve(self, method: str) -> None:
                body = self._read_body()
                parsed = urlparse(self.path)
                target = self.path
                path = parsed.path
                query = parsed.query
                headers = {k.lower(): v for k, v in self.headers.items()}

                token = (headers.get("x-clessira-token") or "").strip()
                ts_raw = (headers.get("x-clessira-timestamp") or "").strip()
                nonce = (headers.get("x-clessira-nonce") or "").strip().lower()
                sig = (headers.get("x-clessira-signature") or "").strip().lower()

                if token != outer.token:
                    return self._send_json(401, {"error": "unauthorized"})

                try:
                    ts = int(ts_raw)
                except ValueError:
                    return self._send_json(401, {"error": "invalid timestamp"})
                if abs(int(time.time()) - ts) > 60:
                    return self._send_json(401, {"error": "expired timestamp"})

                if not (16 <= len(nonce) <= 128) or not nonce.isalnum():
                    return self._send_json(401, {"error": "invalid nonce"})
                if nonce in outer.seen_nonces:
                    return self._send_json(409, {"error": "replay detected"})

                expected = sign_request(
                    token=outer.token,
                    method=method,
                    target=target,
                    timestamp=ts_raw,
                    nonce=nonce,
                    body=body,
                )
                if expected != sig:
                    return self._send_json(401, {"error": "bad signature"})
                outer.seen_nonces.add(nonce)

                request = FakeRequest(method, path, query, body, headers)
                outer.requests.append(request)
                response = outer.handler(request)
                self._send_json(response.status, response.body)

            def do_GET(self) -> None:  # noqa: N802 (BaseHTTPRequestHandler API)
                self._serve("GET")

            def do_POST(self) -> None:  # noqa: N802
                self._serve("POST")

            def _send_json(self, status: int, payload: Any) -> None:
                data = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(data)

        return _Handler


@pytest.fixture
def make_server() -> Iterator[Callable[[str, Handler], FakeServer]]:
    servers: list[FakeServer] = []

    def factory(token: str, handler: Handler) -> FakeServer:
        server = FakeServer(token, handler)
        servers.append(server)
        return server

    yield factory
    for s in servers:
        s.close()
