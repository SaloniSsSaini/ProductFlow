export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = {
  signal?: AbortSignal;
};

export async function apiGet<T>(
  path: string,
  params?: Record<string, string | number | undefined>,
  options?: RequestOptions,
): Promise<T> {
  const searchParams = new URLSearchParams();

  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== "") {
        searchParams.set(key, String(value));
      }
    }
  }

  const query = searchParams.toString();
  const url = query ? `${path}?${query}` : path;

  const response = await fetch(url, { signal: options?.signal });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      // ignore JSON parse errors
    }
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<T>;
}
