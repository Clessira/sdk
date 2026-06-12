# Changelog

All notable changes to `clessira-sdk` (formerly `nowdoing-sdk`) are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com); the project uses
[SemVer](https://semver.org).

## Unreleased

- **BREAKING:** Package renamed from `nowdoing-sdk` to `clessira-sdk` on PyPI.
  Import module changed from `nowdoing` to `clessira` (e.g. `from clessira import ClessiraClient`).
- **BREAKING:** All client classes renamed: `NowDoingClient` → `ClessiraClient`,
  `AsyncNowDoingClient` → `AsyncClessiraClient`; all exception classes renamed
  (`NowDoingError` → `ClessiraError`, `NowDoingAuthError` → `ClessiraAuthError`,
  `NowDoingValidationError` → `ClessiraValidationError`, `NowDoingNotFoundError` →
  `ClessiraNotFoundError`, `NowDoingReplayError` → `ClessiraReplayError`,
  `NowDoingUnavailableError` → `ClessiraUnavailableError`, `NowDoingHttpError` →
  `ClessiraHttpError`).
- **BREAKING:** HTTP request headers renamed: `X-NowDoing-Token` → `X-Clessira-Token`,
  `X-NowDoing-Timestamp` → `X-Clessira-Timestamp`, `X-NowDoing-Nonce` →
  `X-Clessira-Nonce`, `X-NowDoing-Signature` → `X-Clessira-Signature`.
  Requires Mac app with matching wire-protocol update.
- **BREAKING:** Environment variables renamed: `NOWDOING_TOKEN` → `CLESSIRA_TOKEN`,
  `NOWDOING_PORT` → `CLESSIRA_PORT`.
- Repository moved to the Clessira GitHub organization
  (`https://github.com/Clessira/sdk`).
- Pinned runtime + test dependencies to exact versions: `httpx==0.28.1`,
  `pytest==9.0.3`, `pytest-asyncio==1.3.0`.
- Repository/homepage/issues URLs updated to point at `Clessira/sdk`
  (SDK code now lives in its own repo, vendored back into NowDoingMac as a
  submodule).

## 0.1.0 — 2026-05-24

Initial release.

- `NowDoingClient` (sync) and `AsyncNowDoingClient` (async) for the five Mac-app
  endpoints: `healthcheck`, `get_current`, `search_activities`, `start_activity`,
  `notify_branch_change`.
- HMAC-SHA256 request signing with timestamp + nonce replay protection,
  byte-for-byte compatible with `BranchChangeServer` on the Mac side.
- Typed error hierarchy (`NowDoingAuthError`, `NowDoingValidationError`,
  `NowDoingNotFoundError`, `NowDoingReplayError`, `NowDoingUnavailableError`,
  `NowDoingHttpError`, `NowDoingError`).
- `NOWDOING_TOKEN` / `NOWDOING_PORT` env-var fallbacks.
- Tests run against an in-process fake server that re-implements the Mac app's
  auth + replay checks.
