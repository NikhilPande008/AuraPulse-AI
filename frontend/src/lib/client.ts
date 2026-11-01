import type { ApiError } from "../types/plan";

export const API_BASE = "/api/v1";

export function reportError(err: unknown, context?: string): void {
  if (process.env.NODE_ENV === "development") {
    // eslint-disable-next-line no-console
    console.error(context ? `[${context}]` : "[AuraPulse Error]:", err);
  }
}

export function reportWarn(msg: string, ...args: unknown[]): void {
  if (process.env.NODE_ENV === "development") {
    // eslint-disable-next-line no-console
    console.warn("[AuraPulse Warning]:", msg, ...args);
  }
}

export async function parseApiError(res: Response): Promise<ApiError> {
  let errData: {
    code?: string;
    message?: string;
    detail?: string | { message?: string; code?: string };
  } = {};
  try {
    errData = await res.json();
  } catch {
    // Non-JSON response body
  }

  const msg =
    errData.message ||
    (typeof errData.detail === "string" ? errData.detail : errData.detail?.message) ||
    `Request failed with status ${res.status}`;

  const err = new Error(msg) as ApiError;
  err.code =
    errData.code || (typeof errData.detail === "object" ? errData.detail?.code : undefined);
  err.status = res.status;
  return err;
}

export async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit,
  timeoutMs: number = 30000
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(endpoint, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (!res.ok) {
      throw await parseApiError(res);
    }

    return (await res.json()) as T;
  } catch (err) {
    clearTimeout(timeoutId);
    throw err;
  }
}
