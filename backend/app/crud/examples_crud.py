"""
CRUD-операции для таблицы examples (Примеры).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Example, ExampleCategory
from app.schemas import ExampleCreate, ExampleUpdate


def create_example(db: Session, example: ExampleCreate) -> Example:
    """Создать новый пример."""
    db_example = Example(
        summary_id=example.summary_id,
        category=example.category,
        text=example.text,
    )
    db.add(db_example)
    db.commit()
    db.refresh(db_example)
    return db_example


def get_example(db: Session, example_id: int) -> Optional[Example]:
    """Получить один пример по id."""
    return db.query(Example).filter(Example.id == example_id).first()


def get_examples(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    summary_id: Optional[int] = None,
    category: Optional[ExampleCategory] = None,
) -> List[Example]:
    """
    Получить список примеров с пагинацией.
    Опционально можно отфильтровать по id сводки и/или категории.
    """
    query = db.query(Example)
    if summary_id is not None:
        query = query.filter(Example.summary_id == summary_id)
    if category is not None:
        query = query.filter(Example.category == category)
    return query.offset(skip).limit(limit).all()


def update_example(db: Session, example_id: int, example: ExampleUpdate) -> Optional[Example]:
    """Обновить пример (частичное обновление)."""
    db_example = get_example(db, example_id)
    if db_example is None:
        return None

    update_data = example.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_example, field, value)

    db.commit()
    db.refresh(db_example)
    return db_example


def delete_example(db: Session, example_id: int) -> bool:
    """Удалить пример по id. Возвращает True, если удаление произошло."""
    db_example = get_example(db, example_id)
    if db_example is None:
        return False

    db.delete(db_example)
    db.commit()
    return True