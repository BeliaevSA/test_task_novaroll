"""
CRUD-операции для таблицы managers (Менеджеры).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Manager
from app.schemas import ManagerCreate, ManagerUpdate


def create_manager(db: Session, manager: ManagerCreate) -> Manager:
    """Создать нового менеджера."""
    db_manager = Manager(
        first_name=manager.first_name,
        last_name=manager.last_name,
    )
    db.add(db_manager)
    db.commit()
    db.refresh(db_manager)
    return db_manager


def get_manager(db: Session, manager_id: int) -> Optional[Manager]:
    """Получить одного менеджера по id."""
    return db.query(Manager).filter(Manager.id == manager_id).first()


def get_managers(db: Session, skip: int = 0, limit: int = 100) -> List[Manager]:
    """Получить список менеджеров с пагинацией."""
    return db.query(Manager).offset(skip).limit(limit).all()


def update_manager(db: Session, manager_id: int, manager: ManagerUpdate) -> Optional[Manager]:
    """Обновить данные менеджера (частичное обновление)."""
    db_manager = get_manager(db, manager_id)
    if db_manager is None:
        return None

    update_data = manager.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_manager, field, value)

    db.commit()
    db.refresh(db_manager)
    return db_manager


def delete_manager(db: Session, manager_id: int) -> bool:
    """Удалить менеджера по id. Возвращает True, если удаление произошло."""
    db_manager = get_manager(db, manager_id)
    if db_manager is None:
        return False

    db.delete(db_manager)
    db.commit()
    return True