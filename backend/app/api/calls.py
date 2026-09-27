"""
Роуты для работы со звонками на фронте:
- список звонков с фильтром по интервалу дат и менеджерам;
- скачивание исходного .docx с расшифровкой звонка;
- получение сводки звонка в формате {value, examples};
- экспорт сводки звонка в оформленный .docx файл.
"""

from datetime import date
from pathlib import Path
from typing import List, Optional
from urllib.parse import quote
import os

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.crud.calls_crud import get_call, get_calls_filtered
from app.crud.examples_crud import get_examples
from app.crud.summaries_crud import get_summary_by_call_id
from app.database import BASE_DIR, get_db
from app.models import ExampleCategory
from app.schemas import CallListOut, CallSummaryDetailOut, CategoryOut
from app.services.docx_export import build_summary_docx

router = APIRouter(prefix="/calls", tags=["calls"])

FILES_DIR = Path(os.getenv("FILES_DIR", str(BASE_DIR / "files")))

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _resolve_recording_path(call_link: str) -> Path:
    """
    call_link может быть сохранён как:
    - относительный путь, уже включающий "files/..." ;
    - просто имя файла (тогда ищем в BASE_DIR/files).
    - абсолютный путь.
    """
    p = Path(call_link)
    if p.is_absolute():
        return p
    if p.parts and p.parts[0] == "files":
        return FILES_DIR / p.relative_to("files")
    return FILES_DIR / p


def _manager_full_name(first_name: str, last_name: str) -> str:
    return f"{last_name} {first_name}".strip()


@router.get("", response_model=List[CallListOut])
def list_calls(
    date_from: Optional[date] = Query(None, description="Дата ОТ (включительно)"),
    date_to: Optional[date] = Query(None, description="Дата ПО (включительно)"),
    manager_ids: Optional[List[int]] = Query(
        None, description="Список id менеджеров; пусто/не задано = все менеджеры"
    ),
    db: Session = Depends(get_db),
) -> List[CallListOut]:
    """
    Список звонков для таблицы на фронте.

    Правила фильтрации по датам:
    - ничего не выбрано -> отдаём все звонки;
    - выбрана только date_from -> все звонки с этой даты включительно;
    - выбрана только date_to -> все звонки до этой даты включительно;
    - выбраны обе -> звонки внутри интервала включительно.
    """
    calls = get_calls_filtered(db, date_from=date_from, date_to=date_to, manager_ids=manager_ids)

    return [
        CallListOut(
            id=call.id,
            call_datetime=call.call_datetime,
            organization=call.organization,
            duration_seconds=call.duration_seconds,
            manager_id=call.manager_id,
            manager_first_name=call.manager.first_name,
            manager_last_name=call.manager.last_name,
            has_summary=call.summary is not None,
        )
        for call in calls
    ]


@router.get("/{call_id}/recording")
def download_call_recording(call_id: int, db: Session = Depends(get_db)):
    """Скачать исходный .docx файл с расшифровкой звонка."""
    call = get_call(db, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Звонок с указанным call_id не найден")

    file_path = _resolve_recording_path(call.call_link)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Файл расшифровки звонка не найден на сервере")

    return FileResponse(
        path=file_path,
        media_type=DOCX_MEDIA_TYPE,
        filename=file_path.name,
    )


@router.get("/{call_id}/summary", response_model=CallSummaryDetailOut)
def get_call_summary(call_id: int, db: Session = Depends(get_db)) -> CallSummaryDetailOut:
    """Получить сводку звонка в формате {discussion: {value, examples}, ...}."""
    call = get_call(db, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Звонок с указанным call_id не найден")

    summary = get_summary_by_call_id(db, call_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Сводка для этого звонка ещё не сформирована")

    categories: dict[str, CategoryOut] = {}
    for category in (ExampleCategory.discussion, ExampleCategory.agreements, ExampleCategory.risks):
        examples = get_examples(db, summary_id=summary.id, category=category)
        categories[category.value] = CategoryOut(
            value=getattr(summary, category.value) or "",
            examples=[example.text for example in examples],
        )

    return CallSummaryDetailOut(
        id=summary.id,
        call_id=call_id,
        discussion=categories["discussion"],
        agreements=categories["agreements"],
        risks=categories["risks"],
    )


@router.get("/{call_id}/summary/export-docx")
def export_call_summary_docx(call_id: int, db: Session = Depends(get_db)) -> Response:
    """Сформировать и скачать оформленный .docx файл со сводкой звонка."""
    call = get_call(db, call_id)
    if call is None:
        raise HTTPException(status_code=404, detail="Звонок с указанным call_id не найден")

    summary = get_summary_by_call_id(db, call_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Сводка для этого звонка ещё не сформирована")

    summary_dict = {}
    for category in (ExampleCategory.discussion, ExampleCategory.agreements, ExampleCategory.risks):
        examples = get_examples(db, summary_id=summary.id, category=category)
        summary_dict[category.value] = {
            "value": getattr(summary, category.value) or "",
            "examples": [example.text for example in examples],
        }

    manager_full_name = _manager_full_name(call.manager.first_name, call.manager.last_name)

    file_bytes = build_summary_docx(
        manager_full_name=manager_full_name,
        organization=call.organization,
        call_datetime=call.call_datetime,
        duration_seconds=call.duration_seconds,
        summary=summary_dict,
    )

    filename = f"Сводка_{call.organization}_{call.call_datetime.strftime('%Y-%m-%d_%H-%M')}.docx"
    filename_ascii = "summary.docx"

    return Response(
        content=file_bytes,
        media_type=DOCX_MEDIA_TYPE,
        headers={
            # RFC 5987 — корректно передаём кириллицу в имени файла
            "Content-Disposition": (
                f"attachment; filename=\"{filename_ascii}\"; "
                f"filename*=UTF-8''{quote(filename)}"
            )
        },
    )