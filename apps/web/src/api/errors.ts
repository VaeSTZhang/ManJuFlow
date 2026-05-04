type FastApiValidationItem = {
  loc?: Array<string | number>;
  msg?: string;
  type?: string;
};

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function isValidationItem(value: unknown): value is FastApiValidationItem {
  return typeof value === "object" && value !== null;
}

function formatDetail(detail: unknown): string | null {
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .filter(isValidationItem)
      .map((item) => {
        const location = item.loc?.map(String).join(".") || "请求参数";
        const message = item.msg || item.type || "参数校验失败";
        return `${location} ${message}`;
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return `请求参数不完整：${messages.join("；")}`;
    }
  }

  return null;
}

export async function createApiErrorFromResponse(response: Response, fallback: string): Promise<ApiError> {
  try {
    const payload = (await response.json()) as { detail?: unknown };
    const message = formatDetail(payload.detail);
    return new ApiError(message || fallback, response.status);
  } catch {
    return new ApiError(fallback, response.status);
  }
}

export function parseApiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.message.trim()) {
    return error.message;
  }

  return fallback;
}
