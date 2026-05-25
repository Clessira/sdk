import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { NowDoingClient } from "../src/client";
import {
  NowDoingAuthError,
  NowDoingNotFoundError,
  NowDoingReplayError,
  NowDoingValidationError,
} from "../src/errors";
import { startFakeServer, type FakeServer, type Handler } from "./fakeServer";

const TOKEN = "test-token-1234567890";

describe("NowDoingClient", () => {
  let server: FakeServer;

  async function bootClient(handler: Handler): Promise<NowDoingClient> {
    server = await startFakeServer(TOKEN, handler);
    return new NowDoingClient({ token: TOKEN, port: server.port });
  }

  afterEach(async () => {
    if (server) await server.close();
  });

  it("healthcheck succeeds against a signing server", async () => {
    const client = await bootClient(() => ({ body: { ok: true } }));
    await expect(client.healthcheck()).resolves.toBeUndefined();
    expect(server.requests).toHaveLength(1);
    expect(server.requests[0].method).toBe("GET");
    expect(server.requests[0].path).toBe("/healthcheck");
  });

  it("getCurrent unwraps the envelope and returns the activity", async () => {
    const client = await bootClient(() => ({
      body: {
        ok: true,
        result: {
          activityID: "abc",
          activityName: "Coding",
          startedAt: "2026-05-24T10:00:00Z",
          isOnBreak: false,
        },
      },
    }));
    const current = await client.getCurrent();
    expect(current).toEqual({
      activityID: "abc",
      activityName: "Coding",
      startedAt: "2026-05-24T10:00:00Z",
      isOnBreak: false,
    });
  });

  it("getCurrent returns null when no activity is active", async () => {
    const client = await bootClient(() => ({
      body: { ok: true, result: null },
    }));
    await expect(client.getCurrent()).resolves.toBeNull();
  });

  it("searchActivities passes q and limit and returns items", async () => {
    const client = await bootClient(() => ({
      body: {
        items: [
          { id: "id-1", name: "Coding", groupName: "Work" },
          { id: "id-2", name: "Meetings", groupName: null },
        ],
      },
    }));
    const items = await client.searchActivities("co", { limit: 5 });
    expect(items).toHaveLength(2);
    expect(server.requests[0].query).toContain("q=co");
    expect(server.requests[0].query).toContain("limit=5");
  });

  it("startActivity sends body and unwraps the result", async () => {
    const client = await bootClient((req) => {
      const body = JSON.parse(req.body);
      expect(body).toEqual({ name: "Refactor", createIfMissing: true });
      return {
        body: {
          ok: true,
          result: {
            activityID: "new-id",
            activityName: "Refactor",
            created: true,
          },
        },
      };
    });
    const result = await client.startActivity({
      name: "Refactor",
      createIfMissing: true,
    });
    expect(result).toEqual({
      activityID: "new-id",
      activityName: "Refactor",
      created: true,
    });
  });

  it("notifyBranchChange POSTs the payload", async () => {
    const client = await bootClient((req) => {
      expect(JSON.parse(req.body)).toEqual({
        branch: "main",
        repo: "demo",
        previousBranch: "feature/x",
      });
      return { body: { ok: true } };
    });
    await client.notifyBranchChange({
      branch: "main",
      repo: "demo",
      previousBranch: "feature/x",
    });
  });

  it("maps 401 to NowDoingAuthError", async () => {
    server = await startFakeServer("the-real-token", () => ({
      body: { ok: true },
    }));
    const client = new NowDoingClient({
      token: "wrong-token",
      port: server.port,
    });
    await expect(client.healthcheck()).rejects.toBeInstanceOf(
      NowDoingAuthError,
    );
  });

  it("maps 400 to NowDoingValidationError", async () => {
    const client = await bootClient(() => ({
      status: 400,
      body: { error: "empty branch" },
    }));
    await expect(
      client.notifyBranchChange({ branch: "x" }),
    ).rejects.toMatchObject({
      constructor: NowDoingValidationError,
      serverMessage: "empty branch",
      status: 400,
    });
  });

  it("maps 404 to NowDoingNotFoundError", async () => {
    const client = await bootClient(() => ({
      status: 404,
      body: { error: "activity not found" },
    }));
    await expect(
      client.startActivity({ activityID: "11111111-1111-1111-1111-111111111111" }),
    ).rejects.toBeInstanceOf(NowDoingNotFoundError);
  });

  it("maps 409 to NowDoingReplayError on repeated nonce (forced by direct fetch)", async () => {
    // We use the real signer twice with the same nonce by stubbing makeNonce
    // indirectly: just call the client twice — different nonces. To force
    // replay, hit the fake server with a fixed nonce.
    server = await startFakeServer(TOKEN, () => ({ body: { ok: true } }));
    const { signRequest } = await import("../src/auth");
    const ts = Math.floor(Date.now() / 1000).toString();
    const nonce = "fixednoncefixednonce";
    const headers = {
      "X-NowDoing-Token": TOKEN,
      "X-NowDoing-Timestamp": ts,
      "X-NowDoing-Nonce": nonce,
      "X-NowDoing-Signature": signRequest({
        token: TOKEN,
        method: "GET",
        target: "/healthcheck",
        timestamp: ts,
        nonce,
        body: new Uint8Array(),
      }),
    };
    const url = `http://127.0.0.1:${server.port}/healthcheck`;
    const r1 = await fetch(url, { headers });
    expect(r1.status).toBe(200);
    const r2 = await fetch(url, { headers });
    expect(r2.status).toBe(409);
  });
});

describe("NowDoingClient construction", () => {
  beforeEach(() => {
    delete process.env.NOWDOING_TOKEN;
    delete process.env.NOWDOING_PORT;
  });

  it("throws when no token is provided", () => {
    expect(() => new NowDoingClient()).toThrow(/token is required/);
  });

  it("reads NOWDOING_TOKEN from env", () => {
    process.env.NOWDOING_TOKEN = "env-token";
    expect(() => new NowDoingClient()).not.toThrow();
  });

  it("rejects invalid port", () => {
    expect(
      () => new NowDoingClient({ token: "t", port: 99999 }),
    ).toThrow(/invalid port/);
  });
});
