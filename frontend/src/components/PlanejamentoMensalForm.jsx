import { useState } from "react";

const CATEGORIAS_INICIAIS = [
  { nome: "Alimentação", limite: "150", flexivel: false },
  { nome: "Transporte", limite: "100", flexivel: false },
  { nome: "Delivery", limite: "80", flexivel: true },
  { nome: "Lazer", limite: "70", flexivel: true },
  { nome: "Compras", limite: "", flexivel: true },
  { nome: "Assinaturas", limite: "", flexivel: true },
];

const categoriasDoPlanejamento = (planejamento) => {
  if (!planejamento?.categoriasOrdenadas?.length) return CATEGORIAS_INICIAIS;
  return planejamento.categoriasOrdenadas.map((nome) => ({
    nome,
    limite: planejamento.limitesPorCategoria?.[nome] ?? "",
    flexivel: planejamento.categoriasFlexiveis?.includes(nome) || false,
  }));
};

export function PlanejamentoMensalForm({ contaId, competencia, planejamento, onSubmit, loading }) {
  const [renda, setRenda] = useState(() => String(planejamento?.rendaPrevista ?? "500"));
  const [meta, setMeta] = useState(() => String(planejamento?.metaEconomia ?? "100"));
  const [categorias, setCategorias] = useState(() => categoriasDoPlanejamento(planejamento));
  const [novaCategoria, setNovaCategoria] = useState("");
  const [categoriaArrastada, setCategoriaArrastada] = useState("");

  const atualizarCategoria = (nome, alteracao) => {
    setCategorias((atual) => atual.map((categoria) => (
      categoria.nome === nome ? { ...categoria, ...alteracao } : categoria
    )));
  };

  const adicionarCategoria = (event) => {
    event.preventDefault();
    const nome = novaCategoria.trim();
    if (!nome || categorias.some((categoria) => categoria.nome.localeCompare(nome, "pt-BR", { sensitivity: "accent" }) === 0)) return;
    setCategorias((atual) => [...atual, { nome, limite: "", flexivel: false }]);
    setNovaCategoria("");
  };

  const removerCategoria = (nome) => {
    setCategorias((atual) => atual.filter((categoria) => categoria.nome !== nome));
  };

  const reordenar = (destino) => {
    if (!categoriaArrastada || categoriaArrastada === destino) return;
    setCategorias((atual) => {
      const origem = atual.findIndex((categoria) => categoria.nome === categoriaArrastada);
      const destinoIndice = atual.findIndex((categoria) => categoria.nome === destino);
      const proxima = [...atual];
      const [movida] = proxima.splice(origem, 1);
      proxima.splice(destinoIndice, 0, movida);
      return proxima;
    });
    setCategoriaArrastada("");
  };

  const submit = (event) => {
    event.preventDefault();
    const limitesPorCategoria = Object.fromEntries(categorias
      .filter((categoria) => categoria.limite !== "")
      .map((categoria) => [categoria.nome, Number(categoria.limite)]));
    return onSubmit({
      rendaPrevista: Number(renda),
      metaEconomia: Number(meta),
      limitesPorCategoria,
      categoriasFlexiveis: categorias.filter((categoria) => categoria.flexivel).map((categoria) => categoria.nome),
      categoriasOrdenadas: categorias.map((categoria) => categoria.nome),
    });
  };

  return (
    <form onSubmit={submit} className="finance-form">
      <div className="form-row">
        <label className="field"><span>Renda prevista</span><input type="number" min="0.01" step="0.01" required value={renda} onChange={(event) => setRenda(event.target.value)} /></label>
        <label className="field"><span>Meta de economia</span><input type="number" min="0" step="0.01" required value={meta} onChange={(event) => setMeta(event.target.value)} /></label>
      </div>

      <section className="category-manager" aria-label="Tipos de gastos e prioridades">
        <div className="category-manager-heading"><div><b>Tipos de gastos</b><span>Arraste para definir a prioridade: o primeiro é o mais importante.</span></div><span>{categorias.length} tipos</span></div>
        <div className="category-list">
          {categorias.map((categoria, indice) => <div className="category-config" key={categoria.nome} draggable onDragStart={() => setCategoriaArrastada(categoria.nome)} onDragEnd={() => setCategoriaArrastada("")} onDragOver={(event) => event.preventDefault()} onDrop={() => reordenar(categoria.nome)}>
            <button type="button" className="category-drag" aria-label={`Arrastar ${categoria.nome}, prioridade ${indice + 1}`} title="Arraste para reordenar">⋮⋮</button>
            <span className="category-priority">{indice + 1}</span>
            <label className="field"><span>{categoria.nome}</span><input aria-label={`Limite de ${categoria.nome}`} type="number" min="0" step="0.01" value={categoria.limite} onChange={(event) => atualizarCategoria(categoria.nome, { limite: event.target.value })} placeholder="Sem limite" /></label>
            <label className="check"><input type="checkbox" checked={categoria.flexivel} onChange={() => atualizarCategoria(categoria.nome, { flexivel: !categoria.flexivel })} /> flexível</label>
            <button type="button" className="category-remove" onClick={() => removerCategoria(categoria.nome)} aria-label={`Remover ${categoria.nome}`}>×</button>
          </div>)}
        </div>
        <div className="category-create"><label className="field"><span>Novo tipo de gasto</span><input maxLength="60" value={novaCategoria} onChange={(event) => setNovaCategoria(event.target.value)} placeholder="Ex.: Pets" /></label><button type="button" className="button secondary" onClick={adicionarCategoria} disabled={!novaCategoria.trim()}>Adicionar tipo</button></div>
      </section>
      <button className="button primary" disabled={loading || contaId === "" || !competencia || categorias.length === 0}>Salvar planejamento</button>
    </form>
  );
}
