import { useCallback, useEffect, useState } from "react";

const ROTULOS_MOVIMENTO = {
  DEPOSITO: "Depósito",
  RETIRADA: "Retirada",
  RENDIMENTO: "Rendimento",
  EXCLUSAO_RESGATE: "Resgate ao excluir",
};

const CORES_CAIXINHA = [
  { id: "caramelo", nome: "Caramelo" },
  { id: "verde", nome: "Verde ICEI" },
  { id: "azul", nome: "Azul" },
  { id: "roxo", nome: "Roxo" },
  { id: "coral", nome: "Coral" },
];

const formatarDinheiro = (valor) => Number(valor).toLocaleString("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const formatarData = (valor) => new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
}).format(new Date(valor));

export function CaixinhaPanel({ conta, request, loading, onMessage, onContaAtualizada }) {
  const [caixinhas, setCaixinhas] = useState([]);
  const [selecionadaId, setSelecionadaId] = useState("");
  const [pilhaDeModais, setPilhaDeModais] = useState([]);
  const [nome, setNome] = useState("");
  const [cor, setCor] = useState("verde");
  const [valor, setValor] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [modoOrganizacao, setModoOrganizacao] = useState(false);
  const [ordemRascunho, setOrdemRascunho] = useState([]);
  const [caixinhaArrastada, setCaixinhaArrastada] = useState("");

  const carregar = useCallback(async (preferida) => {
    if (!conta) return;
    setCarregando(true);
    try {
      const resultado = await request(`/contas/${conta.id}/caixinhas`);
      setCaixinhas(resultado);
      setSelecionadaId((atual) => preferida ?? (
        resultado.some((item) => item.id === atual) ? atual : resultado[0]?.id || ""
      ));
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

  const executar = async (acao, mensagem, proximaSelecao) => {
    try {
      const resultado = await acao();
      if (resultado?.saldoConta !== undefined && conta) {
        onContaAtualizada({ ...conta, saldo: resultado.saldoConta });
      }
      onMessage(null, mensagem);
      await carregar(typeof proximaSelecao === "function" ? proximaSelecao(resultado) : proximaSelecao);
      return resultado;
    } catch (error) {
      onMessage(error);
      return null;
    }
  };

  if (!conta) return <p className="muted">Selecione uma agência com conta para gerenciar as Caixinhas.</p>;

  const selecionada = caixinhas.find((item) => item.id === selecionadaId);
  const desabilitado = loading || carregando;
  const modal = pilhaDeModais.at(-1) || null;
  const abrirModalRaiz = (proximoModal) => setPilhaDeModais([proximoModal]);
  const abrirSubmodal = (proximoModal) => setPilhaDeModais((atual) => [...atual, proximoModal]);
  const fecharModais = () => setPilhaDeModais([]);
  const voltarModal = () => setPilhaDeModais((atual) => atual.slice(0, -1));

  const abrirCriacao = () => {
    setNome("");
    abrirModalRaiz("criar");
  };

  const abrirEdicao = () => {
    if (!selecionada) return;
    setNome(selecionada.nome);
    abrirSubmodal("editar");
  };

  const abrirGerenciamento = () => {
    if (!selecionada) return;
    setCor(selecionada.cor || "verde");
    abrirSubmodal("gerenciar");
  };

  const abrirDetalhes = (caixinhaId) => {
    setSelecionadaId(caixinhaId);
    setValor("");
    abrirModalRaiz("detalhes");
  };

  const iniciarOrganizacao = () => {
    setOrdemRascunho(caixinhas);
    setModoOrganizacao(true);
  };

  const cancelarOrganizacao = () => {
    setModoOrganizacao(false);
    setOrdemRascunho([]);
    setCaixinhaArrastada("");
  };

  const reordenarRascunho = (destinoId) => {
    if (!caixinhaArrastada || caixinhaArrastada === destinoId) return;
    setOrdemRascunho((atual) => {
      const indiceOrigem = atual.findIndex((item) => item.id === caixinhaArrastada);
      const indiceDestino = atual.findIndex((item) => item.id === destinoId);
      const proxima = [...atual];
      const [movida] = proxima.splice(indiceOrigem, 1);
      proxima.splice(indiceDestino, 0, movida);
      return proxima;
    });
    setCaixinhaArrastada("");
  };

  const moverNaOrdem = (caixinhaId, direcao) => {
    setOrdemRascunho((atual) => {
      const indice = atual.findIndex((item) => item.id === caixinhaId);
      const destino = indice + direcao;
      if (destino < 0 || destino >= atual.length) return atual;
      const proxima = [...atual];
      [proxima[indice], proxima[destino]] = [proxima[destino], proxima[indice]];
      return proxima;
    });
  };

  const salvarOrdem = async () => {
    const resultado = await executar(
      () => request(`/contas/${conta.id}/caixinhas/ordem`, {
        method: "PUT",
        body: { caixinhasIds: ordemRascunho.map((item) => item.id) },
      }),
      "Ordem das Caixinhas atualizada.",
    );
    if (resultado) cancelarOrganizacao();
  };

  const itensExibidos = modoOrganizacao ? ordemRascunho : caixinhas;
  const conteudoDaCaixinha = (item) => <>
    <span className="caixinha-lid" />
    <span className="caixinha-sticker">{item.nome}</span>
    <span className="caixinha-balance">{formatarDinheiro(item.saldo)}</span>
    <span className="caixinha-caption">{modoOrganizacao ? "Arraste para definir a ordem" : "Toque para visualizar"}</span>
  </>;

  return (
    <div className="caixinha-layout">
      <div className="caixinha-toolbar">
        <p className="muted">{modoOrganizacao ? "Arraste as Caixinhas ou use as setas para definir a ordem de exibição." : "Escolha uma Caixinha para acompanhar a reserva e movimentá-la."}</p>
        <div className="caixinha-toolbar-actions">
          {modoOrganizacao ? <><button type="button" className="button secondary" onClick={cancelarOrganizacao} disabled={desabilitado}>Cancelar</button><button type="button" className="button primary" onClick={salvarOrdem} disabled={desabilitado}>Salvar ordem</button></> : <><button type="button" className="button secondary" onClick={iniciarOrganizacao} disabled={desabilitado || caixinhas.length < 2}>Organizar ordem</button><button type="button" className="button primary" onClick={abrirCriacao} disabled={desabilitado}>+ Criar Caixinha</button></>}
        </div>
      </div>

      <div className="caixinha-grid" aria-live="polite">
        {caixinhas.length === 0 && <p className="muted caixinha-empty">Nenhuma Caixinha criada nesta conta.</p>}
        {itensExibidos.map((item, indice) => modoOrganizacao ? <div key={item.id} className={`caixinha-box organizing color-${item.cor || "verde"}`} draggable onDragStart={() => setCaixinhaArrastada(item.id)} onDragEnd={() => setCaixinhaArrastada("")} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); reordenarRascunho(item.id); }}>
          <div className="caixinha-order-controls"><span aria-label={`Posição ${indice + 1}`}>{indice + 1}</span><button type="button" aria-label={`Mover ${item.nome} para cima`} disabled={indice === 0} onClick={() => moverNaOrdem(item.id, -1)}>↑</button><button type="button" aria-label={`Mover ${item.nome} para baixo`} disabled={indice === itensExibidos.length - 1} onClick={() => moverNaOrdem(item.id, 1)}>↓</button></div>
          {conteudoDaCaixinha(item)}
        </div> : <button type="button" key={item.id} className={`caixinha-box color-${item.cor || "verde"} ${selecionadaId === item.id ? "selected" : ""}`} onClick={() => abrirDetalhes(item.id)} aria-pressed={selecionadaId === item.id}>{conteudoDaCaixinha(item)}</button>)}
      </div>

      {modal && <div className="modal-backdrop" role="presentation"><section className={`caixinha-modal ${modal === "detalhes" ? "caixinha-modal-details" : ""}`} role="dialog" aria-modal="true" aria-labelledby="modal-caixinha-titulo"><div className="modal-header"><h3 id="modal-caixinha-titulo">{modal === "criar" ? "Criar Caixinha" : modal === "editar" ? "Editar Caixinha" : modal === "detalhes" ? "Detalhes da Caixinha" : "Gerenciar Caixinha"}</h3>{pilhaDeModais.length > 1 ? <button type="button" className="button ghost modal-back" onClick={voltarModal}>← Voltar</button> : <button type="button" className="button ghost modal-close" onClick={fecharModais} aria-label="Fechar">×</button>}</div>
        {modal === "detalhes" && selecionada && <section className="caixinha-details" aria-live="polite">
          <div className="caixinha-detail-heading"><div><p className="eyebrow">Caixinha selecionada</p><h3>{selecionada.nome}</h3></div><button type="button" className="button ghost" onClick={abrirGerenciamento} disabled={desabilitado}>Gerenciar</button></div>
          <div className="caixinha-metrics"><article><span>Valor armazenado</span><strong>{formatarDinheiro(selecionada.saldo)}</strong></article><article><span>Rendimento acumulado</span><strong>{formatarDinheiro(selecionada.rendimentoTotal)}</strong></article></div>
          <form className="caixinha-movement-form" onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada.id}/guardar`, { method: "POST", body: { valor } }), "Depósito realizado.", selecionada.id).then((resultado) => { if (resultado) setValor(""); }); }}>
            <label className="field"><span>Valor da movimentação</span><input required type="number" min="0.01" step="0.01" value={valor} onChange={(event) => setValor(event.target.value)} placeholder="R$ 0,00" /></label>
            <button className="button primary" disabled={desabilitado}>Depositar</button>
            <button type="button" className="button secondary" disabled={desabilitado || !valor} onClick={() => executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada.id}/resgatar`, { method: "POST", body: { valor } }), "Resgate realizado.", selecionada.id).then((resultado) => { if (resultado) setValor(""); })}>Sacar</button>
          </form>
          <div className="caixinha-history"><h4>Histórico de movimentações</h4>{selecionada.movimentos.length === 0 ? <p className="muted">Ainda não há depósitos, retiradas ou rendimentos.</p> : <ul>{selecionada.movimentos.map((movimento, indice) => <li key={`${movimento.em}-${indice}`}><span className={`movement-dot ${movimento.tipo.toLowerCase()}`} /><div><b>{ROTULOS_MOVIMENTO[movimento.tipo] || movimento.tipo}</b><small>{formatarData(movimento.em)}</small></div><strong className={movimento.tipo === "RETIRADA" ? "negative" : ""}>{movimento.tipo === "RETIRADA" ? "−" : "+"}{formatarDinheiro(movimento.valor)}</strong></li>)}</ul>}</div>
        </section>}
        {modal === "criar" && <form onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas`, { method: "POST", body: { nome } }), "Caixinha criada.", (resultado) => resultado.id).then((resultado) => { if (resultado) fecharModais(); }); }}><label className="field"><span>Nome da Caixinha</span><input autoFocus required maxLength="80" value={nome} onChange={(event) => setNome(event.target.value)} placeholder="Ex.: Viagem" /></label><button className="button primary full" disabled={desabilitado}>Criar</button></form>}
        {modal === "editar" && selecionada && <form onSubmit={(event) => { event.preventDefault(); executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada.id}`, { method: "PATCH", body: { nome } }), "Nome atualizado.", selecionada.id).then((resultado) => { if (resultado) voltarModal(); }); }}><label className="field"><span>Novo nome</span><input autoFocus required maxLength="80" value={nome} onChange={(event) => setNome(event.target.value)} /></label><button className="button primary full" disabled={desabilitado}>Salvar alteração</button></form>}
        {modal === "gerenciar" && selecionada && <div className="manager-actions"><p className="muted">Edite o nome, escolha a cor da caixa ou exclua a Caixinha. Ao excluir, {formatarDinheiro(selecionada.saldo)} será resgatado automaticamente para a conta.</p><button type="button" className="button secondary full" onClick={abrirEdicao} disabled={desabilitado}>Editar nome</button><div className="color-manager"><span>Cor da caixa</span><div className="color-options" role="radiogroup" aria-label="Cor da Caixinha">{CORES_CAIXINHA.map((opcao) => <button type="button" key={opcao.id} className={`color-option color-${opcao.id} ${cor === opcao.id ? "selected" : ""}`} role="radio" aria-checked={cor === opcao.id} onClick={() => setCor(opcao.id)} disabled={desabilitado}><span aria-hidden="true" /><b>{opcao.nome}</b></button>)}</div><button type="button" className="button secondary full" onClick={() => executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada.id}`, { method: "PATCH", body: { cor } }), "Cor da Caixinha atualizada.", selecionada.id).then((resultado) => { if (resultado) voltarModal(); })} disabled={desabilitado || cor === selecionada.cor}>Salvar cor</button></div><button type="button" className="button danger full" onClick={() => executar(() => request(`/contas/${conta.id}/caixinhas/${selecionada.id}`, { method: "DELETE" }), "Caixinha excluída e saldo devolvido à conta.", "").then((resultado) => { if (resultado) fecharModais(); })} disabled={desabilitado}>Excluir e resgatar {formatarDinheiro(selecionada.saldo)}</button></div>}
      </section></div>}
    </div>
  );
}
