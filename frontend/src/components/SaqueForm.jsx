import { useState } from "react";

export function SaqueForm({ defaultConta = "", onSubmit, loading }) {
  const [contaId, setContaId] = useState(defaultConta);
  const [valor, setValor] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    await onSubmit(Number(contaId), Number(valor));
    setValor("");
  };
  return (
    <form className="operation-form" onSubmit={submit}>
      <label className="field"><span>Conta</span><input type="number" min="0" required value={contaId} onChange={(e) => setContaId(e.target.value)} /></label>
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} placeholder="R$ 0,00" /></label>
      <button className="button secondary" disabled={loading}>Sacar</button>
    </form>
  );
}
