"""
CRUD-операции для таблицы calls (Звонки).
"""

from datetime import date, datetime, time, timedelta
from typing import List, Optional, Sequence

from sqlalchemy.orm import Session, joinedload

from app.models import Call, Manager
from app.schemas import CallCreate, CallUpdate


def create_call(db: Session, call: CallCreate) -> Call:
    """Создать новый звонок."""
    db_call = Call(
        call_datetime=call.call_datetime,
        organization=call.organization,
        duration_seconds=call.duration_seconds,
        manager_id=call.manager_id,
        call_link=call.call_link,
    )
    db.add(db_call)
    db.commit()
    db.refresh(db_call)
    return db_call


def get_call(db: Session, call_id: int) -> Optional[Call]:
    """Получить один звонок по id."""
    return db.query(Call).filter(Call.id == call_id).first()


def get_calls(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    manager_id: Optional[int] = None,
    organization: Optional[str] = None,
) -> List[Call]:
    """
    Получить список звонков с пагинацией.
    Опционально можно отфильтровать по менеджеру и/или организации.
    """
    query = db.query(Call)
    if manager_id is not None:
        query = query.filter(Call.manager_id == manager_id)
    if organization is not None:
        query = query.filter(Call.organization == organization)
    return query.order_by(Call.call_datetime.desc()).offset(skip).limit(limit).all()


def get_calls_filtered(
    db: Session,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    manager_ids: Optional[Sequence[int]] = None,
) -> List[Call]:
    """
    Получить список звонков для фронта с фильтрацией по интервалу дат и менеджерам.

    - date_from — включительно, с начала суток.
    - date_to — включительно, до конца суток (23:59:59.999999).
    - manager_ids — если пусто/None, фильтр по менеджерам не применяется
      (эквивалент выбора "Все менеджеры").

    Менеджер подгружается сразу (joinedload), чтобы не делать N+1 запросов
    при формировании ответа с ФИО менеджера.
    """
    query = db.query(Call).options(joinedload(Call.manager))

    if date_from is not None:
        query = query.filter(Call.call_datetime >= datetime.combine(date_from, time.min))

    if date_to is not None:
        # верхняя граница включительно -> берём начало следующих суток и сравниваем строго меньше
        upper_bound = datetime.combine(date_to, time.min) + timedelta(days=1)
        query = query.filter(Call.call_datetime < upper_bound)

    if manager_ids:
        query = query.filter(Call.manager_id.in_(manager_ids))

    return query.order_by(Call.call_datetime.desc()).all()


def update_call(db: Session, call_id: int, call: CallUpdate) -> Optional[Call]:
    """Обновить данные звонка (частичное обновление)."""
    db_call = get_call(db, call_id)
    if db_call is None:
        return None

    update_data = call.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_call, field, value)

    db.commit()
    db.refresh(db_call)
    return db_call


def delete_call(db: Session, call_id: int) -> bool:
    """Удалить звонок по id. Возвращает True, если удаление произошло."""
    db_call = get_call(db, call_id)
    if db_call is None:
        return False

    db.delete(db_call)
    db.commit()
    return True