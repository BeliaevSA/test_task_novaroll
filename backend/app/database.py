"""
Настройка подключения к базе данных SQLite через SQLAlchemy.

Путь к файлу БД берётся из переменной окружения DATABASE_URL
(см. docker-compose.yml). Локально (вне докера) по умолчанию
используется файл ../db/calls.db относительно этого файла.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # корень проекта
DEFAULT_DB_PATH = BASE_DIR / "db" / "calls.db"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# check_same_thread=False необходим для SQLite при работе с FastAPI
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: выдаёт сессию БД и гарантированно закрывает её."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
