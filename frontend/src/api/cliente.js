import { ApiError } from "./erros";

export const AGENCIAS = [
  { id: 0, nome: "Agência 0", url: import.meta.env.VITE_AGENCIA_0_URL || "/api/agencia-0", porta: 4045 },
  { id: 1, nome: "Agência 1", url: import.meta.env.VITE_AGENCIA_1_URL || "/api/agencia-1", porta: 4046 },
  { id: 2, nome: "Agência 2", url: import.meta.env.VITE_AGENCIA_2_URL || "/api/agencia-2", porta: 4047 },
];

export async function apiRequest(
  caminho,
  { agenciaId = 0, token, method = "GET", body, onUnauthorized } = {},
) {
  const agencia = AGENCIAS.find((item) => item.id === Number(agenciaId)) || AGENCIAS[0];
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${agencia.url}${caminho}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError({
      codigo: "AGENCIA_INDISPONIVEL",
      mensagem: `${agencia.nome} não respondeu na porta ${agencia.porta}.`,
      tipo: "rede",
    });
  }

  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new ApiError({
      status: response.status,
      codigo: payload?.codigo || "ERRO_HTTP",
      mensagem: payload?.erro || `A API respondeu com status ${response.status}.`,
      detalhes: payload?.detalhes,
      tipo: response.status === 401 ? "autenticacao" : "negocio",
    });
    if (response.status === 401 && onUnauthorized) onUnauthorized(error);
    throw error;
  }
  return payload;
}
