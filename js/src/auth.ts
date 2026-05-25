import { createHash, createHmac, randomBytes } from "node:crypto";

export interface SignRequestParams {
  token: string;
  method: string;
  target: string;
  timestamp: string;
  nonce: string;
  body: Uint8Array;
}

export function makeNonce(): string {
  // 32 lowercase hex chars — alphanumeric, within the server's 16..128 range.
  return randomBytes(16).toString("hex");
}

export function timestampSeconds(nowMs: number = Date.now()): string {
  return Math.floor(nowMs / 1000).toString();
}

export function sha256Hex(data: Uint8Array): string {
  return createHash("sha256").update(data).digest("hex");
}

export function signRequest(params: SignRequestParams): string {
  const { token, method, target, timestamp, nonce, body } = params;
  const bodyHash = sha256Hex(body);
  const canonical = [
    method.toUpperCase(),
    target,
    timestamp,
    nonce,
    bodyHash,
  ].join("\n");
  return createHmac("sha256", token).update(canonical).digest("hex");
}
