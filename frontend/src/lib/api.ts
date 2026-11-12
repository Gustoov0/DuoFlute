// Cliente HTTP: todas as chamadas à API passam por aqui.
// O endereço é relativo ("/api/..."): o gateway Nginx encaminha para o back-end.

const TOKEN_KEY = "duoflute_token";

export const tokenStorage = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// O FastAPI devolve {"detail": "texto"} ou {"detail": [{"msg": "..."}]} (validação)
function extractMessage(body: unknown): string {
  if (body && typeof body === "object" && "detail" in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg)
            : "Dados inválidos.",
        )
        .join(" ");
    }
  }
  return "Algo deu errado. Tente novamente.";
}

let onUnauthorized: (() => void) | null = null;
/** Chamado quando a API responde 401 (token inválido ou expirado). */
export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorized = handler;
}

interface Options {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

export async function api<T>(path: string, options: Options = {}): Promise<T> {
  const { method = "GET", body, auth = true } = options;

  const headers: Record<string, string> = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = tokenStorage.get();
  if (auth && token) headers["Authorization"] = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "Não foi possível conectar ao servidor.");
  }

  if (!response.ok) {
    let data: unknown = null;
    try {
      data = await response.json();
    } catch {
      /* resposta sem corpo JSON */
    }
    if (response.status === 401 && auth) onUnauthorized?.();
    throw new ApiError(response.status, extractMessage(data));
  }

  return (await response.json()) as T;
}