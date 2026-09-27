import Modal from "./Modal.jsx";

export default function UploadCallModal({ onClose }) {
  return (
    <Modal
      title="Загрузить звонок"
      onClose={onClose}
      footer={
        <button type="button" className="btn btn-primary" onClick={onClose}>
          Понятно
        </button>
      }
    >
      Данный функционал в разработке.
    </Modal>
  );
}