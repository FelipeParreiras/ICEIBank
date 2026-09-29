import { useState } from "react";

const CATEGORIAS = ["MORADIA", "ALIMENTACAO", "TRANSPORTE", "SAUDE", "EDUCACAO", "LAZER", "DELIVERY", "ASSINATURAS", "COMPRAS", "OUTROS"];

export function GastoForm({ contaId, onSubmit, loading }) {
  const [descricao, setDescricao] = useState("");
  const [valor, setValor] = useState("");
  const [categoria, setCategoria] = useState("ALIMENTACAO");
  const [data, setData] = useState(new Date().toISOString().slice(0, 10));
  const submit = async (event) => {
    event.preventDefault();
    await onSubmit({ descricao, valor: Number(valor), categoria, data });
    setDescricao("");
    setValor("");
  };
  return (
    <form onSubmit={submit} className="expense-form">
      <label className="field"><span>Descrição</span><input required maxLength="200" value={descricao} onChange={(e) => setDescricao(e.target.value)} placeholder="Ex.: mercado" /></label>
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} /></label>
      <label className="field"><span>Categoria</span><select value={categoria} onChange={(e) => setCategoria(e.target.value)}>{CATEGORIAS.map((item) => <option key={item}>{item}</option>)}</select></label>
      <label className="field"><span>Data</span><input type="date" required value={data} onChange={(e) => setData(e.target.value)} /></label>
      <button className="button secondary" disabled={loading || contaId === ""}>Registrar gasto</button>
    </form>
  );
}
