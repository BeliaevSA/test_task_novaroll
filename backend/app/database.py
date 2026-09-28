"""
Настройка подключения к базе данных SQLite через SQLAlchemy,
а также путь к папке с файлами записей звонков (/files).

Оба пути можно переопределить переменными окружения (см. docker-compose.yml):
- DATABASE_URL — строка подключения SQLAlchemy к БД.
- FILES_DIR    — абсолютный путь к папке с .docx записями звонков.

Если переменные не заданы (локальный запуск без Docker), используются пути
относительно корня проекта — на уровень выше backend/.
"""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # корень проекта (при локальном запуске)
DEFAULT_DB_PATH = BASE_DIR / "db" / "calls.db"
DEFAULT_FILES_DIR = BASE_DIR / "files"

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")
FILES_DIR = Path(os.getenv("FILES_DIR", str(DEFAULT_FILES_DIR)))

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