"""
Pydantic-схемы для валидации входных/выходных данных CRUD-операций и API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models import ExampleCategory


# ---------- Managers ----------

class ManagerBase(BaseModel):
    first_name: str
    last_name: str


class ManagerCreate(ManagerBase):
    pass


class ManagerUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ManagerOut(ManagerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Calls ----------

class CallBase(BaseModel):
    call_datetime: datetime
    organization: str
    duration_seconds: int
    manager_id: int
    call_link: str


class CallCreate(CallBase):
    pass


class CallUpdate(BaseModel):
    call_datetime: Optional[datetime] = None
    organization: Optional[str] = None
    duration_seconds: Optional[int] = None
    manager_id: Optional[int] = None
    call_link: Optional[str] = None


class CallOut(CallBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CallListOut(BaseModel):
    """Строка таблицы звонков на фронте: список с фильтрацией по дате/менеджерам."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    call_datetime: datetime
    organization: str
    duration_seconds: int
    manager_id: int
    manager_first_name: str
    manager_last_name: str
    has_summary: bool


# ---------- Call summaries ----------

class CallSummaryBase(BaseModel):
    call_id: int
    discussion: Optional[str] = None
    agreements: Optional[str] = None
    risks: Optional[str] = None


class CallSummaryCreate(CallSummaryBase):
    pass


class CallSummaryUpdate(BaseModel):
    discussion: Optional[str] = None
    agreements: Optional[str] = None
    risks: Optional[str] = None


class CallSummaryOut(CallSummaryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Examples ----------

class ExampleBase(BaseModel):
    summary_id: int
    category: ExampleCategory
    text: str


class ExampleCreate(ExampleBase):
    pass


class ExampleUpdate(BaseModel):
    category: Optional[ExampleCategory] = None
    text: Optional[str] = None


class ExampleOut(ExampleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- GenAPI-анализ / ответ клиенту в формате value+examples ----------

MAX_EXAMPLES_PER_CATEGORY = 5


class CategoryAnalysis(BaseModel):
    """Результат анализа по одной категории (discussion / agreements / risks) — из модели."""

    value: str
    examples: List[str] = []

    @staticmethod
    def _clean(v: List[str]) -> List[str]:
        cleaned = [ex for ex in v if isinstance(ex, str) and ex.strip()]
        return cleaned[:MAX_EXAMPLES_PER_CATEGORY]

    def model_post_init(self, __context) -> None:
        self.examples = self._clean(self.examples)


class CallAnalysisResult(BaseModel):
    """Полный результат анализа разговора, ожидаемый от модели."""

    discussion: CategoryAnalysis
    agreements: CategoryAnalysis
    risks: CategoryAnalysis


class CategoryOut(BaseModel):
    """Категория сводки в ответе API: вывод модели + подтверждающие цитаты."""

    value: str
    examples: List[str]


class CallSummaryDetailOut(BaseModel):
    """
    Сводка звонка в формате {discussion: {value, examples}, agreements: {...}, risks: {...}}.
    Используется и как ответ на загрузку .docx, и как ответ на GET сводки по call_id.
    """

    id: int
    call_id: int
    discussion: CategoryOut
    agreements: CategoryOut
    risks: CategoryOut


class CallSummaryDetailWithCallOut(CallSummaryDetailOut):
    """То же самое, но с дополнительной информацией о звонке — для экспорта в docx."""

    call_datetime: datetime
    organization: str
    duration_seconds: int
    manager_first_name: str
    manager_last_name: str