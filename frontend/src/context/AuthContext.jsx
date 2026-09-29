import { createContext, useState } from "react";

import { apiRequest } from "../api/cliente";
import { useAgencia } from "../hooks/useAgencia";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const { agenciaId } = useAgencia();
  const [token, setToken] = useState(() => localStorage.getItem("iceibank.token"));
  const [usuario, setUsuario] = useState(() => localStorage.getItem("iceibank.usuario"));
  const [motivoLogout, setMotivoLogout] = useState("");

  const autenticar = async (caminho, nomeUsuario, dados) => {
    const response = await apiRequest(caminho, {
      agenciaId,
      method: "POST",
      body: { usuario: nomeUsuario, ...dados },
    });
    localStorage.setItem("iceibank.token", response.accessToken);
    localStorage.setItem("iceibank.usuario", nomeUsuario);
    setToken(response.accessToken);
    setUsuario(nomeUsuario);
    setMotivoLogout("");
  };

  const login = (nomeUsuario, senha) => autenticar("/auth/login", nomeUsuario, { senha });
  const cadastrar = (nomeUsuario, senha, confirmarSenha) =>
    autenticar("/auth/cadastro", nomeUsuario, { senha, confirmarSenha });

  const logout = (motivo = "") => {
    localStorage.removeItem("iceibank.token");
    localStorage.removeItem("iceibank.usuario");
    setToken(null);
    setUsuario(null);
    setMotivoLogout(motivo);
  };

  const value = { token, usuario, autenticado: Boolean(token), login, cadastrar, logout, motivoLogout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
