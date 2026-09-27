const API_BASE = "/api";

async function handleResponse(response) {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      // тело ответа не JSON — оставляем statusText
    }
    throw new Error(detail || `Ошибка запроса (${response.status})`);
  }
  return response.json();
}

export async function fetchManagers() {
  const response = await fetch(`${API_BASE}/managers`);
  return handleResponse(response);
}

export async function fetchCalls({ dateFrom, dateTo, managerIds }) {
  const params = new URLSearchParams();
  if (dateFrom) params.set("date_from", dateFrom);
  if (dateTo) params.set("date_to", dateTo);
  if (managerIds && managerIds.length > 0) {
    managerIds.forEach((id) => params.append("manager_ids", id));
  }

  const query = params.toString();
  const response = await fetch(`${API_BASE}/calls${query ? `?${query}` : ""}`);
  return handleResponse(response);
}

export async function fetchCallSummary(callId) {
  const response = await fetch(`${API_BASE}/calls/${callId}/summary`);
  return handleResponse(response);
}

export function getRecordingDownloadUrl(callId) {
  return `${API_BASE}/calls/${callId}/recording`;
}

export function getSummaryExportUrl(callId) {
  return `${API_BASE}/calls/${callId}/summary/export-docx`;
}

/** Скачивание файла по URL средствами браузера (без blob) — сервер сам ставит Content-Disposition. */
export function triggerFileDownload(url) {
  const link = document.createElement("a");
  link.href = url;
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

export async function rebuildCallSummary(callId) {
  const response = await fetch(
    `${API_BASE}/calls/${callId}/summary/rebuild`,
    {
      method: "POST",
    }
  );

  return handleResponse(response);
}