const moeda = (valor) => Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

export function GastosDoMesList({ gastos = [] }) {
  if (!gastos.length) return <p className="muted">Nenhum gasto registrado nesta competência.</p>;
  return (
    <div className="expense-list">
      {gastos.map((gasto) => (
        <div className="expense-item" key={gasto.id}>
          <span className="expense-dot" />
          <div><b>{gasto.descricao}</b><small>{gasto.categoria} · {new Date(`${gasto.data}T12:00:00`).toLocaleDateString("pt-BR")}</small></div>
          <strong>{moeda(gasto.valor)}</strong>
        </div>
      ))}
    </div>
  );
}
