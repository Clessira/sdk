# Clessira SDKs

First-party client SDKs for the [Clessira](https://github.com/Clessira/NowDoingMac)
macOS app's loopback HTTP API. Use them from editor plugins, CLIs, build hooks
or any tool that wants to read the currently-tracked activity or push events
(branch switches, search, start) into the app.

The Mac app exposes a tiny HTTP listener on `127.0.0.1` (default port `39847`),
secured with a per-install shared secret plus HMAC-SHA256 request signing,
replay-safe nonces and a sliding-window rate limit. The SDKs handle all of that
for you — you call the methods, they sign the requests.

| SDK | Package | Runtime | Path |
|---|---|---|---|
| JavaScript / TypeScript | [`@clessira/sdk`](js/README.md) | Node ≥ 20 / Bun / Deno | [`js/`](js/) |
| Python (sync + async) | [`clessira-sdk`](python/README.md) | Python ≥ 3.10 | [`python/`](python/) |

Both SDKs wrap the same five endpoints — `GET /healthcheck`, `GET /current`,
`GET /activities/search`, `POST /activities/start`, `POST /branch-changed` —
with a typed error hierarchy that maps `400 / 401 / 404 / 409 / 503` to
dedicated exception classes, plus env-var fallbacks (`CLESSIRA_TOKEN`,
`CLESSIRA_PORT`).

## Enable the HTTP API

Open **Clessira → Einstellungen → Integrationen → HTTP-API** and turn on
**Aktiviert**. By default the listener stays off — the VSCode extension uses a
separate Unix Domain Socket and doesn't need the TCP listener. Once enabled,
the same shared token is reused; copy it from the Integrationen pane or via
`security find-generic-password -s com.mattes.nowdoing.vscode-token -w`.

## Layout

```
sdks/
├── js/                    @clessira/sdk      — TypeScript, ESM + CJS, vitest
├── python/                clessira-sdk       — sync + async via httpx, pytest
└── .github/workflows/     build + Trusted-Publishing release pipelines
```

## Releases

Each SDK ships independently. Tagging from this repo triggers OIDC-based
Trusted Publishing (no `NPM_TOKEN` / `PYPI_API_TOKEN` secrets):

- `sdk-js-v*`     → `release-sdk-js.yml`     → npm (@clessira/sdk)
- `sdk-python-v*` → `release-sdk-python.yml` → PyPI (clessira-sdk)

Build + test workflows (`sdk-js.yml`, `sdk-python.yml`) run on every push and
PR against the affected SDK's directory.

## Wire-protocol compatibility

The signing layer in both SDKs is verified against shared reference vectors
and an in-process fake server that re-implements the Mac app's signature +
replay checks — so the test suites exercise the real over-the-wire contract,
not mocked transport. The protocol itself lives in `BranchChangeServer.swift`
in the Mac app repo; when it changes, both SDKs must move in lockstep.

## License

Same license as the Mac app — see [NowDoingMac](https://github.com/Clessira/NowDoingMac).
