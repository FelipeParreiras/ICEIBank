import { useCallback, useState } from "react";

import { apiRequest } from "../api/cliente";
import { mensagemAmigavel } from "../api/erros";
import { AgenciaSelector } from "../components/AgenciaSelector";
import { AlertMessage } from "../components/AlertMessage";
import { ContaCard } from "../components/ContaCard";
import { CaixinhaPanel } from "../components/CaixinhaPanel";
import { DepositoForm } from "../components/DepositoForm";
import { GastoForm } from "../components/GastoForm";
import { PlanejamentoMensalForm } from "../components/PlanejamentoMensalForm";
import { ResumoFinanceiro } from "../components/ResumoFinanceiro";
import { SaqueForm } from "../components/SaqueForm";
import { TransferenciaForm } from "../components/TransferenciaForm";
import { useAgencia } from "../hooks/useAgencia";
import { useAuth } from "../hooks/useAuth";
import { useContas } from "../hooks/useContas";

export function DashboardPage() {
  const { token, usuario, logout } = useAuth();
  const { agenciaId, agencia, selecionarAgencia } = useAgencia();
  const listaContas = useContas(agenciaId, token);
  const [conta, setConta] = useState(null);
  const [contaId, setContaId] = useState("0");
  const [nomeAluno, setNomeAluno] = useState("");
  const [saldoInicial, setSaldoInicial] = useState("0");
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  const [financeContaId, setFinanceContaId] = useState("6");
  const [competencia, setCompetencia] = useState("2026-09");
  const [resumo, setResumo] = useState(null);

  const request = useCallback((path, options = {}) =>
    apiRequest(path, {
      agenciaId,
      ...options,
      token,
      onUnauthorized: () => logout("Sua sessão expirou. Entre novamente."),
    }), [agenciaId, logout, token]);

  const executar = async (acao, sucesso, preservarAlert = false) => {
    setLoading(true);
    if (!preservarAlert) setAlert(null);
    try {
      const result = await acao();
      if (sucesso) setAlert({ tipo: "sucesso", mensagem: typeof sucesso === "function" ? sucesso(result) : sucesso });
      return result;
    } catch (error) {
      setAlert({ tipo: error?.codigo === "AGENCIA_DESTINO_INDISPONIVEL" ? "aviso" : "erro", mensagem: mensagemAmigavel(error) });
      return null;
    } finally {
      setLoading(false);
    }
  };

  const consultar = async (event) => {
    event.preventDefault();
    const result = await executar(() => request(`/contas/${Number(contaId)}`));
    if (result) setConta(result);
  };

  const criar = async (event) => {
    event.preventDefault();
    const result = await executar(
      () => request("/contas", { method: "POST", body: { id: Number(contaId), nomeAluno, saldoInicial: Number(saldoInicial) } }),
      "Conta criada com sucesso.",
    );
    if (result) {
      setConta(result);
      listaContas.atualizar();
    }
  };

  const movimentar = async (tipo, id, valor) => {
    const result = await executar(
      () => request(`/contas/${id}/${tipo}`, { method: "POST", body: { valor } }),
      tipo === "depositar" ? "Depósito concluído." : "Saque concluído.",
    );
    if (result) {
      setConta(result);
      setContaId(String(result.id));
    }
    return Boolean(result);
  };

  const transferir = async (origem, destino, valor) => {
    const contaOrigem = listaContas.contas.find((item) => item.id === origem);
    if (!contaOrigem) return false;
    const result = await executar(
      () => request("/transferencias", {
        agenciaId: contaOrigem.agenciaId,
        method: "POST",
        body: { idOrigem: origem, idDestino: destino, valor },
      }),
      (response) => response.mensagem,
    );
    if (result) {
      if (contaOrigem.agenciaId !== agenciaId) {
        selecionarAgencia(contaOrigem.agenciaId);
        setResumo(null);
      }
      if (conta?.id === origem) {
        const atualizada = await executar(() => request(`/contas/${origem}`, { agenciaId: contaOrigem.agenciaId }));
        if (atualizada) setConta(atualizada);
      }
    }
    return Boolean(result);
  };

  const carregarResumo = async (preservarAlert = false) => {
    const result = await executar(
      () => request(`/contas/${Number(financeContaId)}/controle-financeiro/${competencia}`),
      null,
      preservarAlert,
    );
    if (result) setResumo(result);
    return result;
  };

  const salvarPlanejamento = async (dados) => {
    const result = await executar(
      () => request(`/contas/${Number(financeContaId)}/controle-financeiro/${competencia}/planejamento`, { method: "PUT", body: dados }),
      "Planejamento mensal salvo.",
    );
    if (result) await carregarResumo(true);
  };

  const registrarGasto = async (dados) => {
    const result = await executar(
      () => request(`/contas/${Number(financeContaId)}/controle-financeiro/gastos`, { method: "POST", body: dados }),
      "Gasto registrado e debitado da conta.",
    );
    if (result) {
      if (conta?.id === Number(financeContaId)) setConta({ ...conta, saldo: result.saldoConta });
      setCompetencia(dados.data.slice(0, 7));
      const atualizado = await executar(
        () => request(`/contas/${Number(financeContaId)}/controle-financeiro/${dados.data.slice(0, 7)}`),
        null,
        true,
      );
      if (atualizado) setResumo(atualizado);
    }
  };

  const trocarAgencia = () => {
    setConta(null);
    setResumo(null);
    setAlert(null);
  };

  const mensagemCaixinha = useCallback((erro, sucesso) => {
    setAlert(erro ? { tipo: "erro", mensagem: mensagemAmigavel(erro) } : { tipo: "sucesso", mensagem: sucesso });
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><span className="brand-mark small">IB</span><div><b>ICEIBank</b><small>Sprint 1 · RA 45</small></div></div>
        <div className="topbar-actions"><AgenciaSelector disabled={loading} onChange={trocarAgencia} /><div className="user-chip"><span>{usuario?.slice(0, 1).toUpperCase()}</span><div><b>{usuario}</b><small>{agencia.nome}</small></div></div><button className="button ghost" onClick={() => logout()}>Sair</button></div>
      </header>

      <main className="dashboard">
        <section className="hero-row">
          <div><p className="eyebrow">Visão geral</p><h1>Olá, {usuario}. 👋</h1><p className="muted">Gerencie contas e acompanhe sua meta mensal em uma rede distribuída.</p></div>
          <div className="agency-status"><span className="status-dot" /><div><small>Conectado em</small><b>{agencia.nome} · porta {agencia.porta}</b></div></div>
        </section>
        <AlertMessage alert={alert} onClose={() => setAlert(null)} />

        <section className="bank-grid">
          <article className="panel account-panel">
            <div className="section-heading"><div><p className="eyebrow">Conta bancária</p><h2>Saldo e titular</h2></div></div>
            <ContaCard conta={conta} />
            <form className="account-search" onSubmit={consultar}>
              <label className="field"><span>ID da conta</span><input type="number" min="0" required value={contaId} onChange={(e) => setContaId(e.target.value)} /></label>
              <button className="button secondary" disabled={loading}>Consultar</button>
            </form>
            <details className="create-account"><summary>Criar uma nova conta</summary><form onSubmit={criar}><label className="field"><span>Nome do aluno</span><input required value={nomeAluno} onChange={(e) => setNomeAluno(e.target.value)} /></label><label className="field"><span>Saldo inicial</span><input type="number" min="0" step="0.01" value={saldoInicial} onChange={(e) => setSaldoInicial(e.target.value)} /></label><button className="button primary" disabled={loading}>Criar conta</button></form></details>
          </article>

          <article className="panel operations-panel">
            <div className="section-heading"><div><p className="eyebrow">Movimentações</p><h2>Operações rápidas</h2></div></div>
            {listaContas.carregando && <p className="muted" role="status">Carregando contas…</p>}
            {listaContas.erro && <AlertMessage alert={{ tipo: "erro", mensagem: listaContas.erro }} />}
            {!conta && <p className="muted">Consulte uma conta para habilitar depósito e saque.</p>}
            <button type="button" className="button ghost" onClick={listaContas.atualizar} disabled={loading || listaContas.carregando}>Atualizar contas</button>
            <div className="operation-columns"><div><h3><span className="op-icon income">↓</span> Depósito</h3><DepositoForm key={`d-${agenciaId}-${conta?.id}`} conta={conta} onSubmit={(id, valor) => movimentar("depositar", id, valor)} loading={loading} /></div><div><h3><span className="op-icon outcome">↑</span> Saque</h3><SaqueForm key={`s-${agenciaId}-${conta?.id}`} conta={conta} onSubmit={(id, valor) => movimentar("sacar", id, valor)} loading={loading} /></div></div>
            <div className="divider" />
            <div><h3><span className="op-icon transfer">⇄</span> Transferência</h3><TransferenciaForm contas={listaContas.contas} contaSelecionada={conta} onSubmit={transferir} loading={loading || listaContas.carregando} /></div>
          </article>
        </section>

        <section className="panel caixinha-panel">
          <div className="section-heading"><div><p className="eyebrow">Reserva financeira</p><h2>Caixinhas com rendimento</h2><p className="muted">Rendimento composto de 10% a cada 48 horas por depósito.</p></div></div>
          <CaixinhaPanel key={conta?.id ?? "sem-conta"} conta={conta} request={request} loading={loading} onMessage={mensagemCaixinha} onContaAtualizada={setConta} />
        </section>

        <section className="panel finance-panel">
          <div className="section-heading finance-heading"><div><p className="eyebrow">Controle financeiro</p><h2>Meta mensal de economia</h2><p className="muted">Defina quanto quer guardar e receba sugestões transparentes de ajuste.</p></div><div className="finance-filters"><label className="field"><span>Conta</span><input type="number" min="0" value={financeContaId} onChange={(e) => { setFinanceContaId(e.target.value); setResumo(null); }} /></label><label className="field"><span>Competência</span><input type="month" value={competencia} onChange={(e) => { setCompetencia(e.target.value); setResumo(null); }} /></label><button className="button secondary" onClick={() => carregarResumo()} disabled={loading}>Consultar mês</button></div></div>
          <div className="finance-layout">
            <div className="finance-inputs"><details open><summary>1. Planejamento do mês</summary><PlanejamentoMensalForm contaId={financeContaId} competencia={competencia} onSubmit={salvarPlanejamento} loading={loading} /></details><details open><summary>2. Registrar novo gasto</summary><GastoForm contaId={financeContaId} onSubmit={registrarGasto} loading={loading} /></details></div>
            <div className="finance-results"><h3>Análise da meta</h3><ResumoFinanceiro resumo={resumo} /></div>
          </div>
        </section>
      </main>
      <footer><span>ICEIBank · Laboratório de Desenvolvimento de Software</span><span>FastAPI + React + RabbitMQ + relógio vetorial</span></footer>
    </div>
  );
}
