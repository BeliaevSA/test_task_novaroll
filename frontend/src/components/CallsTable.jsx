import { Download, FileSearch, FileX2 } from "lucide-react";
import { getRecordingDownloadUrl, triggerFileDownload } from "../api/client.js";
import { formatDateTime, formatDuration, formatManagerName } from "../utils/format.js";
import "./CallsTable.css";

export default function CallsTable({ calls, onShowSummary }) {
  if (calls.length === 0) {
    return <div className="calls-table__empty">Нет звонков, подходящих под заданные параметры.</div>;
  }

  return (
    <div className="calls-table">
      <div className="calls-table__row calls-table__row--head">
        <span>Дата</span>
        <span>Менеджер</span>
        <span>Организация</span>
        <span>Длительность</span>
        <span className="calls-table__actions-head">Действия</span>
      </div>

      {calls.map((call) => (
        <div className="calls-table__row" key={call.id}>
          <span>{formatDateTime(call.call_datetime)}</span>
          <span>{formatManagerName(call.manager_first_name, call.manager_last_name)}</span>
          <span title={call.organization}>{call.organization}</span>
          <span>{formatDuration(call.duration_seconds)}</span>
          <span className="calls-table__actions">
            <button
              type="button"
              className="icon-btn"
              title="Скачать расшифровку звонка"
              onClick={() => triggerFileDownload(getRecordingDownloadUrl(call.id))}
            >
              <Download size={17} />
            </button>
            <button
              type="button"
              className="icon-btn"
              title={call.has_summary ? "Показать сводку звонка" : "Сводка ещё не сформирована"}
              disabled={!call.has_summary}
              onClick={() => onShowSummary(call)}
            >
              {call.has_summary ? <FileSearch size={17} /> : <FileX2 size={17} />}
            </button>
          </span>
        </div>
      ))}
    </div>
  );
}