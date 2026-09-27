"""
CRUD-операции для таблицы call_summaries (Сводки звонков).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import CallSummary
from app.schemas import CallSummaryCreate, CallSummaryUpdate


def create_summary(db: Session, summary: CallSummaryCreate) -> CallSummary:
    """Создать сводку по звонку (call_id должен быть уникален - одна сводка на звонок)."""
    db_summary = CallSummary(
        call_id=summary.call_id,
        discussion=summary.discussion,
        agreements=summary.agreements,
        risks=summary.risks,
    )
    db.add(db_summary)
    db.commit()
    db.refresh(db_summary)
    return db_summary


def get_summary(db: Session, summary_id: int) -> Optional[CallSummary]:
    """Получить одну сводку по id."""
    return db.query(CallSummary).filter(CallSummary.id == summary_id).first()


def get_summary_by_call_id(db: Session, call_id: int) -> Optional[CallSummary]:
    """Получить сводку по id звонка."""
    return db.query(CallSummary).filter(CallSummary.call_id == call_id).first()


def get_summaries(db: Session, skip: int = 0, limit: int = 100) -> List[CallSummary]:
    """Получить список сводок с пагинацией."""
    return db.query(CallSummary).offset(skip).limit(limit).all()


def update_summary(db: Session, summary_id: int, summary: CallSummaryUpdate) -> Optional[CallSummary]:
    """Обновить сводку звонка (частичное обновление)."""
    db_summary = get_summary(db, summary_id)
    if db_summary is None:
        return None

    update_data = summary.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_summary, field, value)

    db.commit()
    db.refresh(db_summary)
    return db_summary


def delete_summary(db: Session, summary_id: int) -> bool:
    """Удалить сводку по id. Возвращает True, если удаление произошло."""
    db_summary = get_summary(db, summary_id)
    if db_summary is None:
        return False

    db.delete(db_summary)
    db.commit()
    return True