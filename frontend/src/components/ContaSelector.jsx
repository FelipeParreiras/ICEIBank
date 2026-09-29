import { AGENCIAS } from "../api/cliente";

export function ContaSelector({ contas, value, onChange, disabled, label = "Conta" }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select required value={value} onChange={onChange} disabled={disabled || !contas.length}>
        <option value="">{contas.length ? "Selecione uma conta" : "Nenhuma conta cadastrada"}</option>
        {AGENCIAS.map((agencia) => {
          const contasDaAgencia = contas.filter((conta) => conta.agenciaId === agencia.id);
          return contasDaAgencia.length > 0 && (
            <optgroup key={agencia.id} label={agencia.nome}>
              {contasDaAgencia.map((conta) => (
                <option key={conta.id} value={conta.id}>
                  {conta.id} — {conta.nomeAluno} · {agencia.nome}
                </option>
              ))}
            </optgroup>
          );
        })}
      </select>
    </label>
  );
}
