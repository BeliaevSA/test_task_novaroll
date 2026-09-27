"""
ORM-модели для таблиц проекта "Сводка по звонкам".

Таблицы:
    managers        - Менеджеры
    calls           - Звонки
    call_summaries  - Сводки звонков
    examples        - Примеры (категории и все названия столбцов на английском)
"""

import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Manager(Base):
    """Менеджеры."""

    __tablename__ = "managers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)   # имя
    last_name = Column(String(100), nullable=False)    # фамилия

    calls = relationship("Call", back_populates="manager", cascade="all, delete-orphan")


class Call(Base):
    """Звонки."""

    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_datetime = Column(DateTime, nullable=False)          # дата и время звонка (часы, минуты)
    organization = Column(String(255), nullable=False)        # организация
    duration_seconds = Column(Integer, nullable=False)        # продолжительность звонка, сек
    manager_id = Column(Integer, ForeignKey("managers.id", ondelete="CASCADE"), nullable=False)
    call_link = Column(String(500), nullable=False)           # путь/ссылка на файл записи звонка

    manager = relationship("Manager", back_populates="calls")
    summary = relationship(
        "CallSummary",
        back_populates="call",
        uselist=False,
        cascade="all, delete-orphan",
    )


class CallSummary(Base):
    """Сводки звонков."""

    __tablename__ = "call_summaries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_id = Column(
        Integer,
        ForeignKey("calls.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    discussion = Column(Text, nullable=True)   # о чём говорили
    agreements = Column(Text, nullable=True)   # договорённости
    risks = Column(Text, nullable=True)        # риски / потерянные сделки

    call = relationship("Call", back_populates="summary")
    examples = relationship("Example", back_populates="summary", cascade="all, delete-orphan")


class ExampleCategory(str, enum.Enum):
    """Категории примеров - соответствуют столбцам таблицы call_summaries."""

    discussion = "discussion"    # о чём говорили
    agreements = "agreements"    # договорённости
    risks = "risks"              # риски / потерянные сделки


class Example(Base):
    """Примеры (эталонные формулировки по категориям сводки)."""

    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    summary_id = Column(Integer, ForeignKey("call_summaries.id", ondelete="CASCADE"), nullable=False)
    category = Column(Enum(ExampleCategory), nullable=False)
    text = Column(Text, nullable=False)

    summary = relationship("CallSummary", back_populates="examples")
