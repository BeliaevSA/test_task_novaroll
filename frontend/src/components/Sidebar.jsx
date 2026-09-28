import { FileText, NotebookText, PanelLeftClose, PanelLeftOpen, PhoneCall } from "lucide-react";
import "./Sidebar.css";

// Ссылку на GitHub-репозиторий укажите свою — сейчас плейсхолдер.
const GITHUB_URL = "https://github.com/BeliaevSA/test_task_novaroll.git";
const PROMPTS_URL = "/api/files/prompts.pdf";
const INFO_URL = "/api/files/info.pdf";

// lucide-react больше не поставляет брендовые иконки (Github и т.п.) в основном пакете,
// поэтому логотип GitHub — обычный инлайновый SVG, без внешней зависимости.
function GithubIcon({ size = 20 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="currentColor"
      className="sidebar__item-icon"
      aria-hidden="true"
    >
      <path d="M12 .5C5.65.5.5 5.66.5 12.03c0 5.1 3.29 9.42 7.86 10.95.57.11.79-.25.79-.56 0-.27-.01-1.17-.02-2.12-3.2.7-3.88-1.36-3.88-1.36-.52-1.34-1.28-1.7-1.28-1.7-1.04-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.03 1.78 2.7 1.27 3.36.97.1-.75.4-1.27.73-1.56-2.56-.29-5.25-1.29-5.25-5.73 0-1.27.45-2.3 1.19-3.11-.12-.29-.52-1.48.11-3.08 0 0 .97-.31 3.18 1.19a10.9 10.9 0 0 1 5.79 0c2.2-1.5 3.17-1.19 3.17-1.19.63 1.6.24 2.79.12 3.08.74.81 1.18 1.84 1.18 3.11 0 4.45-2.7 5.43-5.27 5.72.41.36.78 1.07.78 2.15 0 1.55-.01 2.8-.01 3.18 0 .31.21.68.8.56A10.97 10.97 0 0 0 23.5 12.03C23.5 5.66 18.35.5 12 .5z" />
    </svg>
  );
}

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={`sidebar ${collapsed ? "sidebar--collapsed" : ""}`}>
      <div className="sidebar__header">
        <button
          type="button"
          className="sidebar__toggle"
          onClick={onToggle}
          title={collapsed ? "Развернуть меню" : "Свернуть меню"}
          aria-label={collapsed ? "Развернуть меню" : "Свернуть меню"}
        >
          {collapsed ? <PanelLeftOpen size={20} /> : <PanelLeftClose size={20} />}
        </button>
      </div>

      <nav className="sidebar__nav">
        <button type="button" className="sidebar__item sidebar__item--active" title="Сводка по звонкам">
          <PhoneCall size={20} className="sidebar__item-icon" />
          {!collapsed && <span className="sidebar__item-text">Сводка по звонкам</span>}
        </button>
      </nav>

      <div className="sidebar__spacer" />

      <nav className="sidebar__nav sidebar__nav--bottom">
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="sidebar__item"
          title="GitHub"
        >
          <GithubIcon size={20} />
          {!collapsed && <span className="sidebar__item-text">GitHub</span>}
        </a>

        <a
          href={PROMPTS_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="sidebar__item"
          title="Промпты"
        >
          <FileText size={20} className="sidebar__item-icon" />
          {!collapsed && <span className="sidebar__item-text">Промпты</span>}
        </a>

        <a
          href={INFO_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="sidebar__item"
          title="Короткая записка"
        >
          <NotebookText size={20} className="sidebar__item-icon" />
          {!collapsed && <span className="sidebar__item-text">Короткая записка</span>}
        </a>
      </nav>
    </aside>
  );
}