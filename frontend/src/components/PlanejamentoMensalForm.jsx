import { useState } from "react";

const CATEGORIAS = ["ALIMENTACAO", "TRANSPORTE", "DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"];
const rotulos = { ALIMENTACAO: "Alimentação", TRANSPORTE: "Transporte", DELIVERY: "Delivery", LAZER: "Lazer", COMPRAS: "Compras", ASSINATURAS: "Assinaturas" };

export function PlanejamentoMensalForm({ contaId, competencia, onSubmit, loading }) {
  const [renda, setRenda] = useState("500");
  const [meta, setMeta] = useState("100");
  const [limites, setLimites] = useState({ ALIMENTACAO: "150", TRANSPORTE: "100", DELIVERY: "80", LAZER: "70" });
  const [flexiveis, setFlexiveis] = useState(["DELIVERY", "LAZER", "COMPRAS", "ASSINATURAS"]);
  const toggle = (categoria) => setFlexiveis((atual) => atual.includes(categoria) ? atual.filter((item) => item !== categoria) : [...atual, categoria]);
  const submit = (event) => {
    event.preventDefault();
    const limitesValidos = Object.fromEntries(Object.entries(limites).filter(([, valor]) => valor !== "").map(([categoria, valor]) => [categoria, Number(valor)]));
    return onSubmit({ rendaPrevista: Number(renda), metaEconomia: Number(meta), limitesPorCategoria: limitesValidos, categoriasFlexiveis: flexiveis });
  };
  return (
    <form onSubmit={submit} className="finance-form">
      <div className="form-row">
        <label className="field"><span>Renda prevista</span><input type="number" min="0.01" step="0.01" required value={renda} onChange={(e) => setRenda(e.target.value)} /></label>
        <label className="field"><span>Meta de economia</span><input type="number" min="0" step="0.01" required value={meta} onChange={(e) => setMeta(e.target.value)} /></label>
      </div>
      <div className="category-grid">
        {CATEGORIAS.map((categoria) => (
          <div className="category-config" key={categoria}>
            <label className="field"><span>{rotulos[categoria]}</span><input aria-label={`Limite de ${rotulos[categoria]}`} type="number" min="0" step="0.01" value={limites[categoria] || ""} onChange={(e) => setLimites({ ...limites, [categoria]: e.target.value })} placeholder="Sem limite" /></label>
            <label className="check"><input type="checkbox" checked={flexiveis.includes(categoria)} onChange={() => toggle(categoria)} /> flexível</label>
          </div>
        ))}
      </div>
      <button className="button primary" disabled={loading || contaId === "" || !competencia}>Salvar planejamento</button>
    </form>
  );
}
