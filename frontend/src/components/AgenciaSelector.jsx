import { AGENCIAS } from "../api/cliente";
import { useAgencia } from "../hooks/useAgencia";
import { SelectField } from "./SelectField";

export function AgenciaSelector({ onChange, disabled = false }) {
  const { agenciaId, selecionarAgencia } = useAgencia();
  const handleChange = (event) => {
    selecionarAgencia(event.target.value);
    onChange?.();
  };
  return (
    <SelectField
      className="compact-field"
      label="Agência ativa"
      value={agenciaId}
      onChange={handleChange}
      disabled={disabled}
    >
        {AGENCIAS.map((agencia) => (
          <option key={agencia.id} value={agencia.id}>
            {agencia.nome} · porta {4045 + agencia.id}
          </option>
        ))}
    </SelectField>
  );
}
