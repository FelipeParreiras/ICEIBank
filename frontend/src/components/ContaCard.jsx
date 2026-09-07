export function ContaCard({ conta }) {
  const formatar = (valor) =>
    Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  if (!conta) {
    return (
      <div className="account-empty">
        <span className="empty-icon">⌁</span>
        <p>Consulte ou crie uma conta para visualizar o saldo.</p>
      </div>
    );
  }
  return (
    <article className="account-card">
      <div>
        <span className="account-label">Saldo disponível</span>
        <strong>{formatar(conta.saldo)}</strong>
      </div>
      <div className="account-owner">
        <span>Conta {conta.id}</span>
        <b>{conta.nomeAluno}</b>
      </div>
    </article>
  );
}
