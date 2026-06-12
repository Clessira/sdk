# clessira-sdk (Python)

Client SDK for the [Clessira](https://github.com/Clessira/NowDoingMac) macOS
app's loopback HTTP API. Use it from CLIs, editor plugins, dotfiles automation,
or any script that wants to read the currently-tracked activity or push
events (branch switches, search, start) into the app.

The Mac app exposes a tiny HTTP listener on `127.0.0.1:39847` (configurable),
secured with a per-install shared secret plus HMAC-SHA256 request signing and
replay protection. This SDK handles all of that for you.

## Install

```sh
pip install clessira-sdk
```

Python ≥ 3.10. The only runtime dependency is `httpx`.

## Enable the HTTP API

Open **Clessira → Einstellungen → Integrationen → HTTP-API** and turn on
**Aktiviert**. By default the listener stays off — the VSCode extension uses a
separate Unix Domain Socket and doesn't need the TCP listener. Once enabled,
Clessira binds an HTTP server on `127.0.0.1` (default port `39847`) using the
same token as the VSCode integration. Pass token and port to the constructor or
set:

```sh
export CLESSIRA_TOKEN="…"
export CLESSIRA_PORT=39847   # optional, default
```

## Quickstart (sync)

```python
from clessira import ClessiraClient

with ClessiraClient() as client:
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
from clessira import AsyncClessiraClient

async def main() -> None:
    async with AsyncClessiraClient() as client:
        current = await client.get_current()
        print(current)

asyncio.run(main())
```

## Errors

All exceptions inherit from `ClessiraError`. HTTP failures map to:

| Status | Exception                    | Typical cause                          |
| -----: | ---------------------------- | -------------------------------------- |
|    400 | `ClessiraValidationError`    | Bad payload (e.g. empty branch).       |
|    401 | `ClessiraAuthError`          | Wrong/missing token or bad signature.  |
|    404 | `ClessiraNotFoundError`      | Activity UUID unknown.                 |
|    409 | `ClessiraReplayError`        | Nonce already used in last 180 s.      |
|    503 | `ClessiraUnavailableError`   | Endpoint handler not wired in the app. |
|  other | `ClessiraHttpError`          | Anything else (incl. 5xx).             |

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

A live smoke test against an actual Clessira instance is gated behind
`-m live`:

```sh
CLESSIRA_TOKEN=… pytest -m live
```

## License

MIT — see the repo root.
