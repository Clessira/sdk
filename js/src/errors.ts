export class NowDoingError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message);
    this.name = "NowDoingError";
    if (options?.cause !== undefined) {
      (this as { cause?: unknown }).cause = options.cause;
    }
  }
}

export class NowDoingHttpError extends NowDoingError {
  readonly status: number;
  readonly serverMessage: string;

  constructor(status: number, serverMessage: string) {
    super(`NowDoing HTTP ${status}: ${serverMessage}`);
    this.name = "NowDoingHttpError";
    this.status = status;
    this.serverMessage = serverMessage;
  }
}

export class NowDoingAuthError extends NowDoingHttpError {
  constructor(status: number, serverMessage: string) {
    super(status, serverMessage);
    this.name = "NowDoingAuthError";
  }
}

export class NowDoingValidationError extends NowDoingHttpError {
  constructor(serverMessage: string) {
    super(400, serverMessage);
    this.name = "NowDoingValidationError";
  }
}

export class NowDoingNotFoundError extends NowDoingHttpError {
  constructor(serverMessage: string) {
    super(404, serverMessage);
    this.name = "NowDoingNotFoundError";
  }
}

export class NowDoingReplayError extends NowDoingHttpError {
  constructor(serverMessage: string) {
    super(409, serverMessage);
    this.name = "NowDoingReplayError";
  }
}

export class NowDoingUnavailableError extends NowDoingHttpError {
  constructor(serverMessage: string) {
    super(503, serverMessage);
    this.name = "NowDoingUnavailableError";
  }
}

export function mapHttpError(
  status: number,
  serverMessage: string,
): NowDoingHttpError {
  switch (status) {
    case 400:
      return new NowDoingValidationError(serverMessage);
    case 401:
      return new NowDoingAuthError(status, serverMessage);
    case 404:
      return new NowDoingNotFoundError(serverMessage);
    case 409:
      return new NowDoingReplayError(serverMessage);
    case 503:
      return new NowDoingUnavailableError(serverMessage);
    default:
      return new NowDoingHttpError(status, serverMessage);
  }
}
