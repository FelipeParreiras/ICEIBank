import { AGENCIAS } from "../api/cliente";
import { useAgencia } from "../hooks/useAgencia";

export function AgenciaSelector({ onChange, disabled = false }) {
  const { agenciaId, selecionarAgencia } = useAgencia();
  const handleChange = (event) => {
    selecionarAgencia(event.target.value);
    onChange?.();
  };
  return (
    <label className="field compact-field">
      <span>Agência ativa</span>
      <select value={agenciaId} onChange={handleChange} disabled={disabled}>
        {AGENCIAS.map((agencia) => (
          <option key={agencia.id} value={agencia.id}>
            {agencia.nome} · porta {4045 + agencia.id}
          </option>
        ))}
      </select>
    </label>
  );
}
