export function formatDateTime(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "—";
 
  const dd = String(date.getDate()).padStart(2, "0");
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const yyyy = date.getFullYear();
  const hh = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
 
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`;
}
 
export function formatDuration(totalSeconds) {
  const seconds = Number(totalSeconds) || 0;
  const minutes = Math.floor(seconds / 60);
  const remainder = seconds % 60;
  return `${minutes} мин ${String(remainder).padStart(2, "0")} сек`;
}
 
export function formatManagerName(firstName, lastName) {
  return `${lastName ?? ""} ${firstName ?? ""}`.trim();
}