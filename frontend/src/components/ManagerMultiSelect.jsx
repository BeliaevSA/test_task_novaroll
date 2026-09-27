import { ChevronDown } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import "./FilterBar.css";
import "./ManagerMultiSelect.css";

export default function ManagerMultiSelect({ managers, selectedIds, onChange }) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const allSelected = managers.length > 0 && selectedIds.length === managers.length;

  function toggleAll() {
    onChange(allSelected ? [] : managers.map((m) => m.id));
  }

  function toggleOne(id) {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter((x) => x !== id));
    } else {
      onChange([...selectedIds, id]);
    }
  }

  let label = "Все менеджеры";
  if (!allSelected && selectedIds.length > 0) {
    label = `Выбрано менеджеров: ${selectedIds.length}`;
  } else if (managers.length === 0) {
    label = "Нет менеджеров";
  }

  return (
    <div className="filter-field" ref={containerRef}>
      <span className="filter-field__label">Менеджер</span>
      <button
        type="button"
        className="manager-select__trigger"
        onClick={() => setOpen((prev) => !prev)}
      >
        <span>{label}</span>
        <ChevronDown size={16} className={`manager-select__chevron ${open ? "manager-select__chevron--open" : ""}`} />
      </button>

      {open && (
        <div className="manager-select__panel">
          <label className="manager-select__option manager-select__option--all">
            <input type="checkbox" checked={allSelected} onChange={toggleAll} />
            <span>Все менеджеры</span>
          </label>

          <div className="manager-select__divider" />

          {managers.map((manager) => (
            <label key={manager.id} className="manager-select__option">
              <input
                type="checkbox"
                checked={selectedIds.includes(manager.id)}
                onChange={() => toggleOne(manager.id)}
              />
              <span>
                {manager.last_name} {manager.first_name}
              </span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}