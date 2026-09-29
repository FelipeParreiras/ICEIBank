import { useState } from "react";

import { mensagemAmigavel } from "../api/erros";
import { AgenciaSelector } from "../components/AgenciaSelector";
import { AlertMessage } from "../components/AlertMessage";
import { PasswordField } from "../components/PasswordField";
import { useAuth } from "../hooks/useAuth";

export function LoginPage() {
  const { login, cadastrar, motivoLogout } = useAuth();
  const [cadastro, setCadastro] = useState(false);
  const [usuario, setUsuario] = useState("aluno");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState(motivoLogout || "");

  const submit = async (event) => {
    event.preventDefault();
    if (cadastro && senha !== confirmarSenha) {
      setErro("As senhas não coincidem.");
      return;
    }
    if (cadastro && !senha.trim()) {
      setErro("A senha não pode conter apenas espaços.");
      return;
    }
    setLoading(true);
    setErro("");
    try {
      if (cadastro) await cadastrar(usuario, senha, confirmarSenha);
      else await login(usuario, senha);
      setSenha("");
      setConfirmarSenha("");
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
            <h2>{cadastro ? "Crie seu usuário" : "Entrar no ICEIBank"}</h2>
            <p className="muted">{cadastro
              ? "Cadastre suas credenciais para acessar o ICEIBank em qualquer agência."
              : "Selecione uma agência e use suas credenciais."}</p>
          </div>
          <AlertMessage alert={erro ? { tipo: "erro", mensagem: erro } : null} />
          <AgenciaSelector disabled={loading} onChange={() => setErro("")} />
          <label className="field">
            <span>Usuário</span>
            <input
              autoComplete="username"
              disabled={loading}
              minLength={cadastro ? 3 : 1}
              maxLength={100}
              pattern={cadastro ? "[a-zA-Z0-9_.\\-]+" : undefined}
              title={cadastro ? "Use letras sem acentos, números, ponto, hífen ou sublinhado." : undefined}
              value={usuario}
              onChange={(event) => setUsuario(event.target.value)}
              required
            />
            {cadastro && <small className="muted">De 3 a 100 caracteres: letras sem acentos, números, ponto, hífen ou sublinhado.</small>}
          </label>
          <PasswordField
              key={cadastro ? "senha-cadastro" : "senha-login"}
              label="Senha"
              hint={cadastro ? "Use pelo menos 8 caracteres." : undefined}
              autoComplete={cadastro ? "new-password" : "current-password"}
              disabled={loading}
              minLength={cadastro ? 8 : 1}
              maxLength={256}
              value={senha}
              onChange={(event) => setSenha(event.target.value)}
              placeholder="Digite sua senha"
              required
            />
          {cadastro && (
              <PasswordField
                label="Confirmar senha"
                autoComplete="new-password"
                value={confirmarSenha}
                onChange={(event) => setConfirmarSenha(event.target.value)}
                minLength={8}
                maxLength={256}
                disabled={loading}
                required
              />
          )}
          <button className="button primary full" disabled={loading}>
            {loading ? (cadastro ? "Cadastrando…" : "Autenticando…")
              : (cadastro ? "Cadastrar e entrar" : "Entrar na conta")}
          </button>
          <button
            type="button"
            className="button ghost full"
            disabled={loading}
            onClick={() => {
              setCadastro(!cadastro);
              setUsuario("");
              setSenha("");
              setConfirmarSenha("");
              setErro("");
            }}
          >
            {cadastro ? "Já tenho usuário. Entrar" : "Não tenho usuário. Cadastrar"}
          </button>
          {!cadastro && <p className="demo-hint">Demonstração: aluno / iceibank123</p>}
        </form>
      </section>
    </main>
  );
}
