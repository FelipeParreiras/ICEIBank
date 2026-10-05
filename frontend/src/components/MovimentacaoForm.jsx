import { useState } from "react";

export function MovimentacaoForm({ conta, onSubmit, loading }) {
  const [tipo, setTipo] = useState("depositar");
  const [valor, setValor] = useState("");

  const submit = async (event) => {
    event.preventDefault();
    if (loading || !conta) return;
    const sucesso = await onSubmit(tipo, conta.id, Number(valor));
    if (sucesso) setValor("");
  };

  return (
    <form className="operation-form quick-movement-form" onSubmit={submit}>
      <label className="field">
        <span>Conta selecionada</span>
        <input value={conta ? `${conta.id} — ${conta.nomeAluno}` : "Consulte uma conta"} readOnly />
      </label>
      <label className="field">
        <span>Tipo de transação</span>
        <select value={tipo} onChange={(event) => setTipo(event.target.value)} disabled={loading || !conta}>
          <option value="depositar">Depósito</option>
          <option value="sacar">Saque</option>
        </select>
      </label>
      <label className="field">
        <span>Valor</span>
        <input type="number" min="0.01" step="0.01" required value={valor} onChange={(event) => setValor(event.target.value)} placeholder="R$ 0,00" />
      </label>
      <button className="button primary" disabled={loading || !conta}>Realizar transação</button>
    </form>
  );
}
