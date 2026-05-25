# Changelog

All notable changes to `@nowdoing/sdk` are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com); the project uses
[SemVer](https://semver.org).

## Unreleased

- Bumped and pinned dev dependencies: `@types/node` 22.19.19, `tsup` 8.5.1,
  `typescript` 5.9.3, `vitest` 4.1.7. Vitest 4 migration was clean (21/21
  pass); TypeScript was pinned to 5.9 because tsup 8.5's DTS pipeline still
  emits a TS 7-deprecated `baseUrl`.
- Repository/homepage/issues URLs updated to point at `NowDoingApp/sdk`
  (SDK code now lives in its own repo, vendored back into NowDoingMac as a
  submodule).

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
