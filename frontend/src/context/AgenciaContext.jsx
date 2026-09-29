import { createContext, useMemo, useState } from "react";

import { AGENCIAS } from "../api/cliente";

export const AgenciaContext = createContext(null);

function agenciaInicial() {
  const stored = Number(localStorage.getItem("iceibank.agencia"));
  return AGENCIAS.some((item) => item.id === stored) ? stored : 0;
}

export function AgenciaProvider({ children }) {
  const [agenciaId, setAgenciaId] = useState(agenciaInicial);
  const selecionarAgencia = (id) => {
    const validId = AGENCIAS.some((item) => item.id === Number(id)) ? Number(id) : 0;
    localStorage.setItem("iceibank.agencia", String(validId));
    setAgenciaId(validId);
  };
  const value = useMemo(
    () => ({
      agenciaId,
      agencia: AGENCIAS.find((item) => item.id === agenciaId),
      selecionarAgencia,
    }),
    [agenciaId],
  );
  return <AgenciaContext.Provider value={value}>{children}</AgenciaContext.Provider>;
}
