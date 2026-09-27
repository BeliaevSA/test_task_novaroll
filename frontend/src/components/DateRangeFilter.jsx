import "./FilterBar.css";

export default function DateRangeFilter({ dateFrom, dateTo, onChangeFrom, onChangeTo }) {
  return (
    <div className="date-range-filter">
      <label className="filter-field">
        <span className="filter-field__label">Дата от</span>
        <input
          type="date"
          className="filter-field__input"
          value={dateFrom}
          max={dateTo || undefined}
          onChange={(e) => onChangeFrom(e.target.value)}
        />
      </label>

      <label className="filter-field">
        <span className="filter-field__label">Дата по</span>
        <input
          type="date"
          className="filter-field__input"
          value={dateTo}
          min={dateFrom || undefined}
          onChange={(e) => onChangeTo(e.target.value)}
        />
      </label>
    </div>
  );
}