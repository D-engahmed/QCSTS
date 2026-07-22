import Select from "react-select";

const selectStyles = {
  control: (base, state) => ({
    ...base,
    borderRadius: "var(--radius)",
    fontSize: "14px",
    borderColor: state.isFocused ? "#0099cc" : "var(--gray-200)",
    borderWidth: "1.5px",
    boxShadow: state.isFocused ? "var(--shadow-sm)" : "none",
    padding: "0px",
    "&:hover": { borderColor: "#0099cc" },
  }),
  option: (base, state) => ({
    ...base,
    backgroundColor: state.isSelected
      ? "var(--primary-light)"
      : state.isFocused
      ? "var(--gray-100)"
      : "white",
    color: state.isSelected ? "white" : "var(--gray-800)",
  }),
};

export default function CustomSelect({ options, value, onChange, placeholder }) {
  return (
    <Select
      styles={selectStyles}
      options={options}
      value={options.find((o) => o.value === value)}
      onChange={(val) => onChange(val?.value)}
      placeholder={placeholder}
    />
  );
}