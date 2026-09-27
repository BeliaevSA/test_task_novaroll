import { PhoneCall, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import "./Sidebar.css";
 
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
    </aside>
  );
}
 