import { useState } from "react";

import { ContaSelector } from "./ContaSelector";

export function TransferenciaForm({ contas, contaSelecionada, onSubmit, loading }) {
  const [origem, setOrigem] = useState("");
  const [destino, setDestino] = useState("");
  const [valor, setValor] = useState("");
  const [erro, setErro] = useState("");

  const origemSelecionada = origem || (contaSelecionada ? String(contaSelecionada.id) : "");
  const submit = async (event) => {
    event.preventDefault();
    if (origemSelecionada === destino) {
      setErro("Origem e destino precisam ser diferentes.");
      return;
    }
    setErro("");
    const sucesso = await onSubmit(Number(origemSelecionada), Number(destino), Number(valor));
    if (sucesso) setValor("");
  };
  return (
    <form className="operation-form transfer-form" onSubmit={submit}>
      <ContaSelector contas={contas} value={origemSelecionada} onChange={(e) => setOrigem(e.target.value)} disabled={loading} label="Origem" />
      <ContaSelector contas={contas} value={destino} onChange={(e) => setDestino(e.target.value)} disabled={loading} label="Destino" />
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} /></label>
      {erro && <p className="field-error">{erro}</p>}
      <button className="button primary" disabled={loading || !origemSelecionada || !destino}>Transferir</button>
    </form>
  );
}
