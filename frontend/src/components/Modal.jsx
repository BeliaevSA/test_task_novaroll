import { X } from "lucide-react";
import { useEffect } from "react";
import "./Modal.css";

export default function Modal({ title, onClose, children, footer }) {
  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  return (
    <div className="modal-overlay" onMouseDown={onClose}>
      <div className="modal-box" onMouseDown={(e) => e.stopPropagation()}>
        <div className="modal-box__header">
          <h3 className="modal-box__title">{title}</h3>
          <button type="button" className="modal-box__close" onClick={onClose} aria-label="Закрыть">
            <X size={18} />
          </button>
        </div>
        <div className="modal-box__body">{children}</div>
        {footer && <div className="modal-box__footer">{footer}</div>}
      </div>
    </div>
  );
}