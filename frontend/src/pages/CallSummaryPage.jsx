import { Upload } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchCalls, fetchManagers } from "../api/client.js";
import CallsTable from "../components/CallsTable.jsx";
import DateRangeFilter from "../components/DateRangeFilter.jsx";
import ManagerMultiSelect from "../components/ManagerMultiSelect.jsx";
import SummaryModal from "../components/SummaryModal.jsx";
import UploadCallModal from "../components/UploadCallModal.jsx";
import "./CallSummaryPage.css";

export default function CallSummaryPage() {
  const [managers, setManagers] = useState([]);
  const [selectedManagerIds, setSelectedManagerIds] = useState([]);

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [calls, setCalls] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [summaryCall, setSummaryCall] = useState(null);

  useEffect(() => {
    fetchManagers()
      .then((data) => {
        setManagers(data);
        // по умолчанию выбраны все менеджеры ("Все менеджеры" отмечено галочкой)
        setSelectedManagerIds(data.map((m) => m.id));
      })
      .catch(() => {
        // список менеджеров не критичен для первой отрисовки — просто оставляем пустым
      });
  }, []);

  async function handleShowClick() {
    setError(null);
    setHasSearched(true);

    // Пользователь вручную снял все галочки менеджеров — по смыслу это
    // "ни один менеджер не выбран", результат должен быть пустым, без запроса к серверу
    // (на бэкенде пустой список менеджеров интерпретируется как "без фильтра" — все менеджеры).
    if (managers.length > 0 && selectedManagerIds.length === 0) {
      setCalls([]);
      return;
    }

    setLoading(true);
    try {
      const allManagersSelected = selectedManagerIds.length === managers.length;
      const data = await fetchCalls({
        dateFrom: dateFrom || undefined,
        dateTo: dateTo || undefined,
        // если выбраны все менеджеры — фильтр по менеджерам не передаём (равнозначно "без фильтра")
        managerIds: allManagersSelected ? [] : selectedManagerIds,
      });
      setCalls(data);
    } catch (err) {
      setError(err.message || "Не удалось загрузить звонки");
      setCalls([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="call-summary-page">
      <div className="call-summary-page__header">
        <h1 className="call-summary-page__title">Сводка по звонкам</h1>
        <button type="button" className="btn btn-primary" onClick={() => setUploadModalOpen(true)}>
          <Upload size={16} />
          Загрузить звонок
        </button>
      </div>

      <div className="call-summary-page__filters">
        <DateRangeFilter
          dateFrom={dateFrom}
          dateTo={dateTo}
          onChangeFrom={setDateFrom}
          onChangeTo={setDateTo}
        />

        <ManagerMultiSelect
          managers={managers}
          selectedIds={selectedManagerIds}
          onChange={setSelectedManagerIds}
        />

        <button type="button" className="btn btn-primary call-summary-page__show-btn" onClick={handleShowClick}>
          {loading ? "Загрузка…" : "Показать"}
        </button>
      </div>

      <div className="call-summary-page__results">
        {error && <div className="call-summary-page__error">{error}</div>}

        {!error && hasSearched && !loading && (
          <CallsTable calls={calls} onShowSummary={setSummaryCall} />
        )}

        {!hasSearched && !loading && (
          <div className="call-summary-page__hint">
            Задайте параметры фильтра (необязательно) и нажмите «Показать», чтобы увидеть звонки.
          </div>
        )}
      </div>

      {uploadModalOpen && <UploadCallModal onClose={() => setUploadModalOpen(false)} />}
      {summaryCall && <SummaryModal call={summaryCall} onClose={() => setSummaryCall(null)} />}
    </div>
  );
}