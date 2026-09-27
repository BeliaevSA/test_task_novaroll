import { useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import CallSummaryPage from "./pages/CallSummaryPage.jsx";
import "./App.css";

export default function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="app-layout">
      <Sidebar collapsed={sidebarCollapsed} onToggle={() => setSidebarCollapsed((prev) => !prev)} />
      <main className="app-content">
        <CallSummaryPage />
      </main>
    </div>
  );
}