export class ClessiraError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message);
    this.name = "ClessiraError";
    if (options?.cause !== undefined) {
      (this as { cause?: unknown }).cause = options.cause;
    }
  }
}

export class ClessiraHttpError extends ClessiraError {
  readonly status: number;
  readonly serverMessage: string;

  constructor(status: number, serverMessage: string) {
    super(`Clessira HTTP ${status}: ${serverMessage}`);
    this.name = "ClessiraHttpError";
    this.status = status;
    this.serverMessage = serverMessage;
  }
}

export class ClessiraAuthError extends ClessiraHttpError {
  constructor(status: number, serverMessage: string) {
    super(status, serverMessage);
    this.name = "ClessiraAuthError";
  }
}

export class ClessiraValidationError extends ClessiraHttpError {
  constructor(serverMessage: string) {
    super(400, serverMessage);
    this.name = "ClessiraValidationError";
  }
}

export class ClessiraNotFoundError extends ClessiraHttpError {
  constructor(serverMessage: string) {
    super(404, serverMessage);
    this.name = "ClessiraNotFoundError";
  }
}

export class ClessiraReplayError extends ClessiraHttpError {
  constructor(serverMessage: string) {
    super(409, serverMessage);
    this.name = "ClessiraReplayError";
  }
}

export class ClessiraUnavailableError extends ClessiraHttpError {
  constructor(serverMessage: string) {
    super(503, serverMessage);
    this.name = "ClessiraUnavailableError";
  }
}

export function mapHttpError(
  status: number,
  serverMessage: string,
): ClessiraHttpError {
  switch (status) {
    case 400:
      return new ClessiraValidationError(serverMessage);
    case 401:
      return new ClessiraAuthError(status, serverMessage);
    case 404:
      return new ClessiraNotFoundError(serverMessage);
    case 409:
      return new ClessiraReplayError(serverMessage);
    case 503:
      return new ClessiraUnavailableError(serverMessage);
    default:
      return new ClessiraHttpError(status, serverMessage);
  }
}
