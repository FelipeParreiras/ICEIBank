import { useState } from "react";

import { SelectField } from "./SelectField";

export function GastoForm({ contaId, categorias = [], onSubmit, loading }) {
  const [descricao, setDescricao] = useState("");
  const [valor, setValor] = useState("");
  const [categoria, setCategoria] = useState("");
  const [data, setData] = useState(new Date().toISOString().slice(0, 10));

  const categoriaSelecionada = categorias.includes(categoria) ? categoria : categorias[0] || "";
  const submit = async (event) => {
    event.preventDefault();
    await onSubmit({ descricao, valor: Number(valor), categoria: categoriaSelecionada, data });
    setDescricao("");
    setValor("");
  };
  return (
    <form onSubmit={submit} className="expense-form">
      <label className="field"><span>Descrição</span><input required maxLength="200" value={descricao} onChange={(e) => setDescricao(e.target.value)} placeholder="Ex.: mercado" /></label>
      <label className="field"><span>Valor</span><input type="number" min="0.01" step="0.01" required value={valor} onChange={(e) => setValor(e.target.value)} /></label>
      <SelectField
        label="Categoria"
        required
        value={categoriaSelecionada}
        onChange={(event) => setCategoria(event.target.value)}
        disabled={categorias.length === 0}
      >
        {categorias.length === 0
          ? <option value="">Salve o planejamento primeiro</option>
          : categorias.map((item) => <option key={item}>{item}</option>)}
      </SelectField>
      <label className="field"><span>Data</span><input type="date" required value={data} onChange={(e) => setData(e.target.value)} /></label>
      <button className="button secondary" disabled={loading || contaId === "" || !categoriaSelecionada}>Registrar gasto</button>
    </form>
  );
}
