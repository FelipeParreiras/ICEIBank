import { GastosDoMesList } from "./GastosDoMesList";
import { RecomendacoesEconomia } from "./RecomendacoesEconomia";

const moeda = (valor) => Number(valor || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export function ResumoFinanceiro({ resumo }) {
  if (!resumo) return <div className="finance-empty"><span>◎</span><p>Salve um planejamento e consulte o mês para ver a análise.</p></div>;
  const progresso = Math.min(100, Math.max(0, (Number(resumo.totalGasto) / Number(resumo.limiteGastoMensal || 1)) * 100));
  return (
    <div className="finance-summary">
      <div className="metric-grid">
        <article><span>Limite mensal</span><strong>{moeda(resumo.limiteGastoMensal)}</strong></article>
        <article><span>Total gasto</span><strong>{moeda(resumo.totalGasto)}</strong></article>
        <article><span>Economia projetada</span><strong>{moeda(resumo.economiaProjetada)}</strong></article>
        <article className={Number(resumo.valorAjuste) > 0 ? "attention" : "positive"}><span>Ajuste necessário</span><strong>{moeda(resumo.valorAjuste)}</strong></article>
      </div>
      <div className="budget-progress"><div style={{ width: `${progresso}%` }} /><span>{progresso.toFixed(0)}% do limite utilizado</span></div>
      <RecomendacoesEconomia recomendacoes={resumo.recomendacoes} valorNaoCoberto={resumo.valorNaoCoberto} />
      <div><h4>Gastos do mês</h4><GastosDoMesList gastos={resumo.gastos} /></div>
      <p className="disclaimer">Recomendações matemáticas baseadas nos limites informados; não constituem aconselhamento financeiro.</p>
    </div>
  );
}
