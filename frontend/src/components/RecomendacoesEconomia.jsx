const moeda = (valor) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export function RecomendacoesEconomia({ recomendacoes, valorNaoCoberto }) {
  if (!recomendacoes?.length) {
    return <div className="goal-ok">✓ Sua meta continua atingível com os gastos registrados.</div>;
  }
  return (
    <div className="recommendations">
      <h4>Onde você pode economizar</h4>
      {recomendacoes.map((item) => (
        <article key={item.categoria} className="recommendation">
          <div><b>{item.categoria}</b><span>{item.motivo === "ACIMA_DO_LIMITE" ? "Acima do limite definido" : "Maior gasto flexível"}</span></div>
          <strong>− {moeda(item.reducaoSugerida)}</strong>
        </article>
      ))}
      {Number(valorNaoCoberto) > 0 && <p className="field-error">Ainda faltam {moeda(valorNaoCoberto)} sem categoria flexível para corte.</p>}
    </div>
  );
}
