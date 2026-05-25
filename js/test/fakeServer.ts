import { createServer, type Server } from "node:http";
import type { AddressInfo } from "node:net";
import { signRequest } from "../src/auth";

export interface HandledRequest {
  method: string;
  path: string;
  query: string;
  body: string;
  headers: Record<string, string | undefined>;
}

export interface FakeResponse {
  status?: number;
  body?: unknown;
}

export type Handler = (req: HandledRequest) => FakeResponse | Promise<FakeResponse>;

export interface FakeServer {
  port: number;
  requests: HandledRequest[];
  close(): Promise<void>;
}

/**
 * Spins up a loopback HTTP server that re-implements the Mac app's auth check
 * (HMAC signature + replay nonce + 60s timestamp window) so SDK tests verify
 * the real over-the-wire contract, not just method calls.
 */
export async function startFakeServer(
  token: string,
  handler: Handler,
): Promise<FakeServer> {
  const seenNonces = new Set<string>();
  const requests: HandledRequest[] = [];

  const server: Server = createServer((req, res) => {
    void (async () => {
      const chunks: Buffer[] = [];
      for await (const chunk of req) chunks.push(chunk as Buffer);
      const body = Buffer.concat(chunks).toString("utf8");

      const method = (req.method ?? "GET").toUpperCase();
      const target = req.url ?? "/";
      const [path, query = ""] = target.split("?", 2) as [string, string?];

      const headers = req.headers as Record<string, string | undefined>;
      const headerToken = headers["x-nowdoing-token"]?.trim() ?? "";
      const headerTs = headers["x-nowdoing-timestamp"]?.trim() ?? "";
      const headerNonce = headers["x-nowdoing-nonce"]?.trim().toLowerCase() ?? "";
      const headerSig = headers["x-nowdoing-signature"]?.trim().toLowerCase() ?? "";

      const respond = (status: number, payload: unknown): void => {
        const out = JSON.stringify(payload);
        res.writeHead(status, {
          "content-type": "application/json; charset=utf-8",
          "content-length": Buffer.byteLength(out).toString(),
          connection: "close",
        });
        res.end(out);
      };

      if (headerToken !== token) {
        respond(401, { error: "unauthorized" });
        return;
      }
      const ts = Number.parseInt(headerTs, 10);
      if (!Number.isFinite(ts)) {
        respond(401, { error: "invalid timestamp" });
        return;
      }
      if (Math.abs(Date.now() / 1000 - ts) > 60) {
        respond(401, { error: "expired timestamp" });
        return;
      }
      if (!/^[0-9a-z]{16,128}$/.test(headerNonce)) {
        respond(401, { error: "invalid nonce" });
        return;
      }
      if (seenNonces.has(headerNonce)) {
        respond(409, { error: "replay detected" });
        return;
      }
      const expected = signRequest({
        token,
        method,
        target,
        timestamp: headerTs,
        nonce: headerNonce,
        body: new TextEncoder().encode(body),
      });
      if (expected !== headerSig) {
        respond(401, { error: "bad signature" });
        return;
      }
      seenNonces.add(headerNonce);

      const request: HandledRequest = { method, path, query, body, headers };
      requests.push(request);
      const result = await handler(request);
      respond(result.status ?? 200, result.body ?? { ok: true });
    })().catch((err) => {
      // eslint-disable-next-line no-console
      console.error("fake server handler error:", err);
      try {
        res.writeHead(500, { "content-type": "application/json" });
        res.end(JSON.stringify({ error: "internal" }));
      } catch {
        // already destroyed
      }
    });
  });

  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = (server.address() as AddressInfo).port;

  return {
    port,
    requests,
    close: () =>
      new Promise<void>((resolve) => {
        server.close(() => resolve());
      }),
  };
}
