import { useCallback, useEffect, useState } from "react";

export function CaixinhaPanel({ conta, request, loading, onMessage, onContaAtualizada }) {
  const [caixinhas, setCaixinhas] = useState([]);
  const [selecionada, setSelecionada] = useState("");
  const [nome, setNome] = useState("");
  const [valor, setValor] = useState("");
  const [carregando, setCarregando] = useState(false);

  const carregar = useCallback(async () => {
    if (!conta) return;
    setCarregando(true);
    try {
      const resultado = await request(`/contas/${conta.id}/caixinhas`);
      setCaixinhas(resultado);
      setSelecionada((atual) => resultado.some((item) => item.id === atual) ? atual : resultado[0]?.id || "");
    } catch (error) {
      onMessage(error);
    } finally {
      setCarregando(false);
    }
  }, [conta, onMessage, request]);

  useEffect(() => {
    if (!conta) return undefined;
    const timer = window.setTimeout(() => void carregar(), 0);
    return () => window.clearTimeout(timer);
  }, [conta, carregar]);

  const executar = async (acao, mensagem) => {
    try {
      const resultado = await acao();
      if (resultado?.saldoConta && conta) onContaAtualizada({ ...conta, saldo: resultado.saldoConta });
      onMessage(null, mensagem);
      await carregar();
    } catch (error) {
      onMessage(error);
    }
  };

  if (!conta) return <p className="muted">Consulte uma conta para gerenciar as Caixinhas.</p>;

  const desabilitado = loading || carregando;
  return (
    <div className="caixinha-layout">
      <form className="inline-form" onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas`, { method: "POST", body: { nome } }), "Caixinha criada."); setNome(""); }}>
        <label className="field"><span>Nova Caixinha</span><input required maxLength="80" value={nome} onChange={(event) => setNome(event.target.value)} placeholder="Ex.: Viagem" /></label>
        <button className="button primary" disabled={desabilitado}>Criar</button>
      </form>
      <div className="caixinha-list" aria-live="polite">
        {caixinhas.length === 0 && <p className="muted">Nenhuma Caixinha criada nesta conta.</p>}
        {caixinhas.map((item) => <button type="button" key={item.id} className={`caixinha-item ${selecionada === item.id ? "selected" : ""}`} onClick={() => setSelecionada(item.id)}><span>{item.nome}</span><b>R$ {item.saldo}</b></button>)}
      </div>
      {selecionada && <div className="caixinha-actions">
        <form className="inline-form" onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada}`, { method: "PATCH", body: { nome } }), "Nome da Caixinha atualizado."); }}>
          <label className="field"><span>Renomear selecionada</span><input required maxLength="80" value={nome} onChange={(event) => setNome(event.target.value)} placeholder="Novo nome" /></label>
          <button className="button secondary" disabled={desabilitado}>Renomear</button>
          <button type="button" className="button ghost" disabled={desabilitado} onClick={() => executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada}`, { method: "DELETE" }), "Caixinha excluída.")}>Excluir</button>
        </form>
        <form className="inline-form" onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada}/guardar`, { method: "POST", body: { valor } }), "Valor guardado na Caixinha."); setValor(""); }}>
          <label className="field"><span>Valor</span><input required type="number" min="0.01" step="0.01" value={valor} onChange={(event) => setValor(event.target.value)} /></label>
          <button className="button primary" disabled={desabilitado}>Guardar</button>
          <button type="button" className="button secondary" disabled={desabilitado || !valor} onClick={() => executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada}/resgatar`, { method: "POST", body: { valor } }), "Resgate concluído.")}>Resgatar</button>
        </form>
      </div>}
    </div>
  );
}
