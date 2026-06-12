import json

import pytest

from clessira import (
    ActivitySearchItem,
    AsyncClessiraClient,
    CurrentActivity,
    ClessiraAuthError,
    ClessiraClient,
    ClessiraError,
    ClessiraNotFoundError,
    ClessiraReplayError,
    ClessiraValidationError,
)

from .conftest import FakeResponse

TOKEN = "test-token-1234567890"


def test_healthcheck(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={"ok": True}))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        client.healthcheck()
    assert len(server.requests) == 1
    assert server.requests[0].path == "/healthcheck"


def test_get_current_returns_activity(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={
        "ok": True,
        "result": {
            "activityID": "abc",
            "activityName": "Coding",
            "startedAt": "2026-05-24T10:00:00Z",
            "isOnBreak": False,
        },
    }))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        current = client.get_current()
    assert current == CurrentActivity(
        activity_id="abc",
        activity_name="Coding",
        started_at="2026-05-24T10:00:00Z",
        is_on_break=False,
    )


def test_get_current_returns_none_when_no_activity(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={"ok": True, "result": None}))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        assert client.get_current() is None


def test_search_activities_passes_query(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={"items": [
        {"id": "id-1", "name": "Coding", "groupName": "Work"},
        {"id": "id-2", "name": "Meetings", "groupName": None},
    ]}))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        items = client.search_activities("co", limit=5)
    assert items == [
        ActivitySearchItem(id="id-1", name="Coding", group_name="Work"),
        ActivitySearchItem(id="id-2", name="Meetings", group_name=None),
    ]
    assert "q=co" in server.requests[0].query
    assert "limit=5" in server.requests[0].query


def test_start_activity_sends_body_and_unwraps(make_server):
    captured: dict = {}

    def handler(req):
        captured["body"] = json.loads(req.body.decode())
        return FakeResponse(body={"ok": True, "result": {
            "activityID": "new-id",
            "activityName": "Refactor",
            "created": True,
        }})

    server = make_server(TOKEN, handler)
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        result = client.start_activity(name="Refactor", create_if_missing=True)

    assert captured["body"] == {"createIfMissing": True, "name": "Refactor"}
    assert result.activity_id == "new-id"
    assert result.created is True


def test_start_activity_requires_id_or_name(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse())
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        with pytest.raises(ClessiraError, match="activity_id or name"):
            client.start_activity()


def test_notify_branch_change_posts_payload(make_server):
    captured: dict = {}

    def handler(req):
        captured["body"] = json.loads(req.body.decode())
        return FakeResponse(body={"ok": True})

    server = make_server(TOKEN, handler)
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        client.notify_branch_change(branch="main", repo="demo", previous_branch="feat/x")

    assert captured["body"] == {"branch": "main", "repo": "demo", "previousBranch": "feat/x"}


def test_notify_branch_change_rejects_empty_branch(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse())
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        with pytest.raises(ClessiraError, match="branch is required"):
            client.notify_branch_change(branch="   ")


def test_wrong_token_raises_auth_error(make_server):
    server = make_server("real-token", lambda req: FakeResponse())
    with ClessiraClient(token="wrong-token", port=server.port) as client:
        with pytest.raises(ClessiraAuthError):
            client.healthcheck()


def test_400_raises_validation_error(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(status=400, body={"error": "empty branch"}))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        with pytest.raises(ClessiraValidationError) as exc:
            client.notify_branch_change(branch="x")
    assert exc.value.server_message == "empty branch"


def test_404_raises_not_found(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(status=404, body={"error": "activity not found"}))
    with ClessiraClient(token=TOKEN, port=server.port) as client:
        with pytest.raises(ClessiraNotFoundError):
            client.start_activity(activity_id="11111111-1111-1111-1111-111111111111")


def test_replay_protection_triggers_409(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={"ok": True}))
    import httpx
    from clessira._auth import sign_request

    ts = str(__import__("time").time().__trunc__())
    nonce = "fixednoncefixednonce"
    target = "/healthcheck"
    sig = sign_request(token=TOKEN, method="GET", target=target,
                       timestamp=ts, nonce=nonce, body=b"")
    headers = {
        "X-Clessira-Token": TOKEN,
        "X-Clessira-Timestamp": ts,
        "X-Clessira-Nonce": nonce,
        "X-Clessira-Signature": sig,
    }
    url = f"http://127.0.0.1:{server.port}{target}"
    assert httpx.get(url, headers=headers).status_code == 200
    assert httpx.get(url, headers=headers).status_code == 409
    # ensure the SDK surfaces it as ClessiraReplayError when it ever encounters one
    # (synthetic: by reusing the same nonce we already used, the next SDK call would
    # still get a fresh nonce; this is purely a server-side smoke test.)
    assert issubclass(ClessiraReplayError, Exception)


def test_construction_requires_token(monkeypatch):
    monkeypatch.delenv("CLESSIRA_TOKEN", raising=False)
    monkeypatch.delenv("CLESSIRA_PORT", raising=False)
    with pytest.raises(ClessiraError, match="token is required"):
        ClessiraClient()


def test_env_token_is_used(monkeypatch):
    monkeypatch.setenv("CLESSIRA_TOKEN", "env-token")
    client = ClessiraClient()
    client.close()


def test_invalid_port_rejected(monkeypatch):
    monkeypatch.delenv("CLESSIRA_PORT", raising=False)
    with pytest.raises(ClessiraError, match="invalid port"):
        ClessiraClient(token="t", port=99999)


async def test_async_get_current(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={
        "ok": True,
        "result": {
            "activityID": "abc",
            "activityName": "Coding",
            "startedAt": "2026-05-24T10:00:00Z",
            "isOnBreak": True,
        },
    }))
    async with AsyncClessiraClient(token=TOKEN, port=server.port) as client:
        current = await client.get_current()
    assert current is not None
    assert current.is_on_break is True


async def test_async_start_activity(make_server):
    server = make_server(TOKEN, lambda req: FakeResponse(body={
        "ok": True,
        "result": {"activityID": "id", "activityName": "Coding", "created": False},
    }))
    async with AsyncClessiraClient(token=TOKEN, port=server.port) as client:
        result = await client.start_activity(name="Coding")
    assert result.created is False
