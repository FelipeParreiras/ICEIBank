import { useState } from "react";

export function TransferenciaForm({ onSubmit, loading }) {
  const [origem, setOrigem] = useState("");
  const [destino, setDestino] = useState("");
  const [valor, setValor] = useState("");
  const [erro, setErro] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    if (origem === destino) {
      setErro("Origem e destino precisam ser diferentes.");
      return;
    }
    setErro("");
    await onSubmit(Number(origem), Number(destino), Number(valor));
    setValor("");
  };
  return (
    <form className="operation-form transfer-form" onSubmit={submit}>
      <label className="field"><span>Origem</span><input type="number" min="0" required value={origem} onChange={(e) => setOrigem(e.target.value)} /></label>
      <label className="field"><span>Destino</span><input type="number" min="0" required value={destino} onChange={(e) => setDestino(e.target.value)} /></label>
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} /></label>
      {erro && <p className="field-error">{erro}</p>}
      <button className="button primary" disabled={loading}>Transferir</button>
    </form>
  );
}
