import { useState } from "react";

import { mensagemAmigavel } from "../api/erros";
import { AgenciaSelector } from "../components/AgenciaSelector";
import { AlertMessage } from "../components/AlertMessage";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login, motivoLogout } = useAuth();
  const [usuario, setUsuario] = useState("aluno");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(motivoLogout || "");

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setErro("");
    try {
      await login(usuario, senha);
      setSenha("");
    } catch (error) {
      setErro(mensagemAmigavel(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="login-shell">
      <section className="login-brand" aria-label="Apresentação do ICEIBank">
        <div className="brand-mark">IB</div>
        <p className="eyebrow">Laboratório de sistemas distribuídos</p>
        <h1>Seu dinheiro, seus eventos, uma ordem lógica.</h1>
        <p>
          Três agências cooperando com FastAPI, React e relógios de Lamport — agora com metas
          mensais de economia.
        </p>
        <div className="network-preview" aria-hidden="true">
          <span>A0</span><i /><span>A1</span><i /><span>A2</span>
        </div>
      </section>
      <section className="login-panel">
        <form className="login-card" onSubmit={submit}>
          <div>
            <p className="eyebrow">Área segura</p>
            <h2>Entrar no ICEIBank</h2>
            <p className="muted">Selecione uma agência e use suas credenciais.</p>
          </div>
          <AlertMessage alert={erro ? { tipo: "erro", mensagem: erro } : null} />
          <AgenciaSelector onChange={() => setErro("")} />
          <label className="field">
            <span>Usuário</span>
            <input
              autoComplete="username"
              value={usuario}
              onChange={(event) => setUsuario(event.target.value)}
              required
            />
          </label>
          <label className="field">
            <span>Senha</span>
            <input
              type="password"
              autoComplete="current-password"
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              placeholder="Digite sua senha"
              required
            />
          </label>
          <button className="button primary full" disabled={loading}>
            {loading ? "Autenticando…" : "Entrar na conta"}
          </button>
          <p className="demo-hint">Demonstração: aluno / iceibank123</p>
        </form>
      </section>
    </main>
  );
}
