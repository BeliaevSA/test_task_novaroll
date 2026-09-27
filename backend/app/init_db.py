"""
Скрипт создания всех таблиц в базе данных.

Запуск локально:
    cd backend
    python -m app.init_db

Запуск в контейнере:
    docker compose exec backend python -m app.init_db
"""

from app.database import Base, engine
from app import models  # noqa: F401  (регистрирует модели в metadata)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы (или уже существовали).")


if __name__ == "__main__":
    init_db()
