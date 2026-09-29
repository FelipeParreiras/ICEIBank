import { useContext } from "react";

import { AgenciaContext } from "../context/AgenciaContext";

export function useAgencia() {
  const context = useContext(AgenciaContext);
  if (!context) throw new Error("useAgencia deve ser usado dentro de AgenciaProvider.");
  return context;
}
