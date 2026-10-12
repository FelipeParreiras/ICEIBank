export function SelectField({
  label,
  className = "",
  children,
  ...selectProps
}) {
  const fieldClassName = ["field", "select-field", className].filter(Boolean).join(" ");

  return (
    <label className={fieldClassName}>
      {label && <span>{label}</span>}
      <span className="select-control">
        <select {...selectProps}>{children}</select>
      </span>
    </label>
  );
}
