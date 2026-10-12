import { Children, isValidElement, useEffect, useId, useMemo, useRef, useState } from "react";

function extrairOpcoes(children) {
  return Children.toArray(children).flatMap((child) => {
    if (!isValidElement(child)) return [];
    if (child.type === "optgroup") {
      return Children.toArray(child.props.children)
        .filter(isValidElement)
        .map((option) => ({
          grupo: child.props.label,
          label: option.props.children,
          value: String(option.props.value ?? option.props.children),
        }));
    }
    return [{
      grupo: null,
      label: child.props.children,
      value: String(child.props.value ?? child.props.children),
    }];
  });
}

export function SelectField({
  label,
  className = "",
  children,
  value,
  onChange,
  disabled = false,
  scrollable = false,
  ...selectProps
}) {
  const [aberto, setAberto] = useState(false);
  const containerRef = useRef(null);
  const listboxId = useId();
  const opcoes = useMemo(() => extrairOpcoes(children), [children]);
  const valorSelecionado = String(value ?? "");
  const selecionada = opcoes.find((option) => option.value === valorSelecionado) ?? opcoes[0];
  const fieldClassName = ["field", "select-field", className].filter(Boolean).join(" ");

  useEffect(() => {
    const fecharAoClicarFora = (event) => {
      if (!containerRef.current?.contains(event.target)) setAberto(false);
    };
    document.addEventListener("pointerdown", fecharAoClicarFora);
    return () => document.removeEventListener("pointerdown", fecharAoClicarFora);
  }, []);

  const selecionar = (opcao) => {
    setAberto(false);
    if (opcao.value !== valorSelecionado) onChange?.({ target: { value: opcao.value } });
  };

  const navegar = (event) => {
    if (disabled) return;
    if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)) {
      event.preventDefault();
      setAberto(true);
    }
    if (event.key === "Escape") setAberto(false);
  };

  return (
    <div className={fieldClassName} ref={containerRef}>
      {label && <span>{label}</span>}
      <button
        aria-controls={listboxId}
        aria-expanded={aberto}
        aria-haspopup="listbox"
        aria-label={`${label}: ${selecionada?.label ?? "Nenhuma opção"}`}
        className="select-control"
        disabled={disabled}
        onClick={() => setAberto((atual) => !atual)}
        onKeyDown={navegar}
        type="button"
        {...selectProps}
      >
        <span>{selecionada?.label}</span>
        <span aria-hidden="true" className="select-icon" />
      </button>
      {aberto && (
        <div
          aria-label={label}
          className={`select-menu${scrollable ? " select-menu-scrollable" : ""}`}
          id={listboxId}
          role="listbox"
        >
          {opcoes.map((opcao, indice) => (
            <div className="select-menu-item" key={`${opcao.grupo}-${opcao.value}`}>
              {opcao.grupo && (indice === 0 || opcoes[indice - 1].grupo !== opcao.grupo) && (
                <span className="select-group">{opcao.grupo}</span>
              )}
              <button
                aria-selected={opcao.value === valorSelecionado}
                className={opcao.value === valorSelecionado ? "selected" : ""}
                onClick={() => selecionar(opcao)}
                role="option"
                type="button"
              >
                {opcao.label}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
