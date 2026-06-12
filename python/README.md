# nowdoing-sdk (Python)

Client SDK for the [NowDoing](https://github.com/Clessira/NowDoingMac) macOS
app's loopback HTTP API. Use it from CLIs, editor plugins, dotfiles automation,
or any script that wants to read the currently-tracked activity or push
events (branch switches, search, start) into the app.

The Mac app exposes a tiny HTTP listener on `127.0.0.1:39847` (configurable),
secured with a per-install shared secret plus HMAC-SHA256 request signing and
replay protection. This SDK handles all of that for you.

## Install

```sh
pip install nowdoing-sdk
```

Python ≥ 3.10. The only runtime dependency is `httpx`.

## Enable the HTTP API

Open **NowDoing → Einstellungen → Integrationen → HTTP-API** and turn on
**Aktiviert**. By default the listener stays off — the VSCode extension uses a
separate Unix Domain Socket and doesn't need the TCP listener. Once enabled,
NowDoing binds an HTTP server on `127.0.0.1` (default port `39847`) using the
same token as the VSCode integration. Pass token and port to the constructor or
set:

```sh
export NOWDOING_TOKEN="…"
export NOWDOING_PORT=39847   # optional, default
```

## Quickstart (sync)

```python
from nowdoing import NowDoingClient

with NowDoingClient() as client:
    client.healthcheck()

    current = client.get_current()
    if current is None:
        print("Nothing running.")
    else:
        print(f"On: {current.activity_name} (since {current.started_at})")

    hits = client.search_activities("co", limit=5)
    for hit in hits:
        print(f"  {hit.name}  [{hit.group_name or 'no group'}]")

    started = client.start_activity(name="Refactor", create_if_missing=True)
    print(f"Started {started.activity_name} (created={started.created})")

    client.notify_branch_change(
        branch="feature/sdk-rewrite",
        repo="nowdoingmac",
        previous_branch="main",
    )
```

## Async client

```python
import asyncio
from nowdoing import AsyncNowDoingClient

async def main() -> None:
    async with AsyncNowDoingClient() as client:
        current = await client.get_current()
        print(current)

asyncio.run(main())
```

## Errors

All exceptions inherit from `NowDoingError`. HTTP failures map to:

| Status | Exception                    | Typical cause                          |
| -----: | ---------------------------- | -------------------------------------- |
|    400 | `NowDoingValidationError`    | Bad payload (e.g. empty branch).       |
|    401 | `NowDoingAuthError`          | Wrong/missing token or bad signature.  |
|    404 | `NowDoingNotFoundError`      | Activity UUID unknown.                 |
|    409 | `NowDoingReplayError`        | Nonce already used in last 180 s.      |
|    503 | `NowDoingUnavailableError`   | Endpoint handler not wired in the app. |
|  other | `NowDoingHttpError`          | Anything else (incl. 5xx).             |

Each carries `status: int` and `server_message: str`.

## API

| Method                                                  | Endpoint                |
| ------------------------------------------------------- | ----------------------- |
| `healthcheck()`                                         | `GET  /healthcheck`     |
| `get_current() -> CurrentActivity \| None`              | `GET  /current`         |
| `search_activities(q, *, limit=None) -> list[…]`        | `GET  /activities/search` |
| `start_activity(*, activity_id=…, name=…, create_if_missing=False)` | `POST /activities/start` |
| `notify_branch_change(*, branch, repo=…, previous_branch=…)` | `POST /branch-changed`  |

## Running the tests

```sh
pip install -e ".[test]"
pytest
```

The unit tests boot a tiny in-process HTTP server that re-implements the
Mac app's signature + replay checks, so they exercise the real over-the-wire
contract — not mocked transport.

A live smoke test against an actual NowDoing instance is gated behind
`-m live`:

```sh
NOWDOING_TOKEN=… pytest -m live
```

## License

MIT — see the repo root.
