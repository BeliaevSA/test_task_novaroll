"""
Роут: список менеджеров (для мультиселекта с чекбоксами на фронте).
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.managers_crud import get_managers
from app.database import get_db
from app.schemas import ManagerOut

router = APIRouter(prefix="/managers", tags=["managers"])


@router.get("", response_model=List[ManagerOut])
def list_managers(db: Session = Depends(get_db)) -> List[ManagerOut]:
    """Вернуть всех менеджеров (лимит с запасом — их немного)."""
    return get_managers(db, skip=0, limit=1000)