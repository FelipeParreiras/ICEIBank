import { createContext, useState } from "react";

import { apiRequest } from "../api/cliente";
import { useAgencia } from "../hooks/useAgencia";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { agenciaId } = useAgencia();
  const [token, setToken] = useState(() => localStorage.getItem("iceibank.token"));
  const [usuario, setUsuario] = useState(() => localStorage.getItem("iceibank.usuario"));
  const [motivoLogout, setMotivoLogout] = useState("");

  const login = async (nomeUsuario, senha) => {
    const response = await apiRequest("/auth/login", {
      agenciaId,
      method: "POST",
      body: { usuario: nomeUsuario, senha },
    });
    localStorage.setItem("iceibank.token", response.accessToken);
    localStorage.setItem("iceibank.usuario", nomeUsuario);
    setToken(response.accessToken);
    setUsuario(nomeUsuario);
    setMotivoLogout("");
  };

  const logout = (motivo = "") => {
    localStorage.removeItem("iceibank.token");
    localStorage.removeItem("iceibank.usuario");
    setToken(null);
    setUsuario(null);
    setMotivoLogout(motivo);
  };

  const value = { token, usuario, autenticado: Boolean(token), login, logout, motivoLogout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
