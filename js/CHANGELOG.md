# Changelog

All notable changes to `@nowdoing/sdk` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com); the project uses
[SemVer](https://semver.org).

## 0.1.0 — 2026-05-24

Initial release.

- `NowDoingClient` for the five Mac-app endpoints: `healthcheck`, `getCurrent`,
  `searchActivities`, `startActivity`, `notifyBranchChange`.
- HMAC-SHA256 request signing with timestamp + nonce replay protection,
  byte-for-byte compatible with `BranchChangeServer` on the Mac side.
- Typed error hierarchy (`NowDoingAuthError`, `NowDoingValidationError`,
  `NowDoingNotFoundError`, `NowDoingReplayError`, `NowDoingUnavailableError`,
  `NowDoingHttpError`, `NowDoingError`).
- `NOWDOING_TOKEN` / `NOWDOING_PORT` env-var fallbacks.
- ESM + CJS dual build with TypeScript type definitions.
- Tests run against an in-process Node HTTP server that re-implements the Mac
  app's auth + replay checks.
