import { Download, RefreshCw, X } from "lucide-react";
import { useEffect, useState } from "react";
import {
  fetchCallSummary,
  rebuildCallSummary,
  getSummaryExportUrl,
  triggerFileDownload,
} from "../api/client.js";
import { formatDateTime, formatDuration, formatManagerName } from "../utils/format.js";
import "./SummaryModal.css";

const SECTIONS = [
  { key: "discussion", title: "О чём говорили" },
  { key: "agreements", title: "Договорённости" },
  { key: "risks", title: "Риски / потерянные сделки" },
];

export default function SummaryModal({ call, onClose }) {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);

  const handleRebuild = async () => {
    try {
      setRebuilding(true);
      setError(null);

      const data = await rebuildCallSummary(call.id);

      setSummary(data);
    } catch (err) {
      setError(err.message || "Не удалось пересобрать сводку");
    } finally {
      setRebuilding(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    fetchCallSummary(call.id)
      .then((data) => {
        if (!cancelled) {
          setSummary(data);
          setError(null);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err.message || "Не удалось загрузить сводку");
          setSummary(null);
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [call.id]);

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div className="summary-modal">
      <div className="summary-modal__header">
        <div>
          <h2 className="summary-modal__title">Сводка звонка</h2>
          <div className="summary-modal__meta">
            {formatDateTime(call.call_datetime)} · {formatManagerName(call.manager_first_name, call.manager_last_name)}{" "}
            · {call.organization} · {formatDuration(call.duration_seconds)}
          </div>
        </div>
        <button type="button" className="summary-modal__close" onClick={onClose} aria-label="Закрыть">
          <X size={22} />
        </button>
      </div>

      <div className="summary-modal__body">
        {loading && <div className="summary-modal__state">Загрузка сводки…</div>}
        {!loading && error && <div className="summary-modal__state summary-modal__state--error">{error}</div>}

        {!loading &&
          !error &&
          summary &&
          SECTIONS.map(({ key, title }) => {
            const category = summary[key] || { value: "", examples: [] };
            return (
              <section className="summary-section" key={key}>
                <h3 className="summary-section__title">{title}</h3>
                <div className="summary-section__columns">
                  <div className="summary-section__value">
                    <div className="summary-section__col-label">Вывод</div>
                    <p>{category.value || "Информация отсутствует."}</p>
                  </div>
                  <div className="summary-section__examples">
                    <div className="summary-section__col-label">Примеры из разговора</div>
                    {category.examples && category.examples.length > 0 ? (
                      <ul>
                        {category.examples.map((example, idx) => (
                          <li key={idx}>«{example}»</li>
                        ))}
                      </ul>
                    ) : (
                      <p className="summary-section__no-examples">Примеры отсутствуют.</p>
                    )}
                  </div>
                </div>
              </section>
            );
          })}
      </div>

      <div className="summary-modal__footer">
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onClose}
          disabled={rebuilding}
        >
          Закрыть
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleRebuild}
          disabled={loading || rebuilding}
        >
          <RefreshCw
            size={16}
            className={rebuilding ? "summary-modal__spinner" : ""}
          />
          {rebuilding ? "Пересобираем…" : "Пересобрать сводку"}
        </button>

        <button
          type="button"
          className="btn btn-primary"
          disabled={loading || !!error || rebuilding}
          onClick={() =>
            triggerFileDownload(getSummaryExportUrl(call.id))
          }
        >
          <Download size={16} />
          Скачать сводку
        </button>
      </div>
    </div>
  );
}