import { useId, useState } from "react";

export function PasswordField({ label, hint, ...inputProps }) {
  const id = useId();
  const [visivel, setVisivel] = useState(false);

  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      <div className="password-field">
        <input
          {...inputProps}
          id={id}
          type={visivel ? "text" : "password"}
          aria-describedby={hint ? `${id}-hint` : undefined}
        />
        <button
          type="button"
          className="password-toggle"
          aria-label={`${visivel ? "Ocultar" : "Mostrar"} ${label.toLowerCase()}`}
          aria-controls={id}
          aria-pressed={visivel}
          disabled={inputProps.disabled}
          onClick={() => setVisivel(!visivel)}
        >
          {visivel ? "Ocultar" : "Mostrar"}
        </button>
      </div>
      {hint && <small id={`${id}-hint`} className="muted">{hint}</small>}
    </div>
  );
}
