import { useState } from "react";

export function DepositoForm({ conta, onSubmit, loading }) {
  const [valor, setValor] = useState("");
  const submit = async (event) => {
    event.preventDefault();
    if (loading || !conta) return;
    const sucesso = await onSubmit(conta.id, Number(valor));
    if (sucesso) setValor("");
  };
  return (
    <form className="operation-form" onSubmit={submit}>
      <label className="field"><span>Conta selecionada</span><input value={conta ? `${conta.id} — ${conta.nomeAluno}` : "Consulte uma conta"} readOnly /></label>
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} placeholder="R$ 0,00" /></label>
      <button className="button secondary" disabled={loading || !conta}>Depositar</button>
    </form>
  );
}
