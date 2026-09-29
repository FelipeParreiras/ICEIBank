export function AlertMessage({ alert, onClose }) {
  if (!alert) return null;
  return (
    <div className={`alert alert-${alert.tipo || "info"}`} role="alert">
      <span>{alert.mensagem}</span>
      {onClose && (
        <button type="button" className="alert-close" onClick={onClose} aria-label="Fechar aviso">
          ×
        </button>
      )}
    </div>
  );
}
