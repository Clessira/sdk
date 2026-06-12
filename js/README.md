# @clessira/sdk (JavaScript / TypeScript)

Client SDK for the [Clessira](https://github.com/Clessira/NowDoingMac) macOS
app's loopback HTTP API. Use it from editor plugins, CLIs, build hooks, or any
Node / Bun / Deno tool that wants to read the currently-tracked activity or
push events (branch switches, search, start) into the app.

The Mac app exposes a tiny HTTP listener on `127.0.0.1:39847` (configurable),
secured with a per-install shared secret plus HMAC-SHA256 request signing and
replay protection. This SDK handles all of that for you.

## Install

```sh
npm install @clessira/sdk
# or
pnpm add @clessira/sdk
# or
bun add @clessira/sdk
```

Node ≥ 20 (uses built-in `fetch` and `node:crypto`; Node 18 went EOL in April 2025). Browser is intentionally
unsupported — the listener binds to loopback and most browsers refuse CORS to
`127.0.0.1`.

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

## Quickstart

```ts
import { ClessiraClient } from "@clessira/sdk";

const client = new ClessiraClient();

await client.healthcheck();

const current = await client.getCurrent();
if (current === null) {
  console.log("Nothing running.");
} else {
  console.log(`On: ${current.activityName} (since ${current.startedAt})`);
}

const hits = await client.searchActivities("co", { limit: 5 });
for (const hit of hits) {
  console.log(`  ${hit.name}  [${hit.groupName ?? "no group"}]`);
}

const started = await client.startActivity({
  name: "Refactor",
  createIfMissing: true,
});
console.log(`Started ${started.activityName} (created=${started.created})`);

await client.notifyBranchChange({
  branch: "feature/sdk-rewrite",
  repo: "nowdoingmac",
  previousBranch: "main",
});
```

## Errors

All exceptions inherit from `ClessiraError`. HTTP failures map to:

| Status | Class                       | Typical cause                          |
| -----: | --------------------------- | -------------------------------------- |
|    400 | `ClessiraValidationError`   | Bad payload (e.g. empty branch).       |
|    401 | `ClessiraAuthError`         | Wrong/missing token or bad signature.  |
|    404 | `ClessiraNotFoundError`     | Activity UUID unknown.                 |
|    409 | `ClessiraReplayError`       | Nonce already used in last 180 s.      |
|    503 | `ClessiraUnavailableError`  | Endpoint handler not wired in the app. |
|  other | `ClessiraHttpError`         | Anything else (incl. 5xx).             |

Each carries `status: number` and `serverMessage: string`.

## API

| Method                                                            | Endpoint                  |
| ----------------------------------------------------------------- | ------------------------- |
| `healthcheck()`                                                   | `GET  /healthcheck`       |
| `getCurrent(): Promise<CurrentActivity \| null>`                  | `GET  /current`           |
| `searchActivities(q, { limit? }): Promise<ActivitySearchItem[]>`  | `GET  /activities/search` |
| `startActivity({ activityID?, name?, createIfMissing? })`         | `POST /activities/start`  |
| `notifyBranchChange({ branch, repo?, previousBranch? })`          | `POST /branch-changed`    |

## Running the tests

```sh
npm install
npm test
```

The unit tests boot a tiny in-process Node HTTP server that re-implements the
Mac app's signature + replay checks, so they exercise the real over-the-wire
contract — not mocked transport.

## License

MIT — see the repo root.
